import base64
import os
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import litellm
from litellm import completion, completion_cost
from litellm.exceptions import (
    APIConnectionError,
    RateLimitError,
    ServiceUnavailableError,
)
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from app.config import LLMSettings, config
from app.llm.cost import Cost
from app.logger import logger
from app.schema import Message


class LLM:
    _instances: Dict[str, "LLM"] = {}

    def __new__(
        cls, config_name: str = "default", llm_config: Optional[LLMSettings] = None
    ):
        if config_name not in cls._instances:
            instance = super().__new__(cls)
            instance.__init__(config_name, llm_config)
            cls._instances[config_name] = instance
        return cls._instances[config_name]

    def __init__(
        self, config_name: str = "default", llm_config: Optional[LLMSettings] = None
    ):
        if not hasattr(
            self, "initialized"
        ):  # Only initialize if not already initialized
            llm_config = llm_config or config.llm
            llm_config = llm_config.get(config_name, llm_config["default"])

            self.model = getattr(llm_config, "model", "gpt-3.5-turbo")
            self.max_tokens = getattr(llm_config, "max_tokens", 4096)
            self.temperature = getattr(llm_config, "temperature", 0.7)
            self.top_p = getattr(llm_config, "top_p", 0.9)
            self.api_type = getattr(llm_config, "api_type", "openai")
            self.api_key = getattr(
                llm_config, "api_key", os.environ.get("OPENAI_API_KEY", "")
            )
            self.api_version = getattr(llm_config, "api_version", "")
            self.base_url = getattr(llm_config, "base_url", "https://api.openai.com/v1")
            self.timeout = getattr(llm_config, "timeout", 60)
            self.num_retries = getattr(llm_config, "num_retries", 3)
            self.retry_min_wait = getattr(llm_config, "retry_min_wait", 1)
            self.retry_max_wait = getattr(llm_config, "retry_max_wait", 10)
            self.custom_llm_provider = getattr(llm_config, "custom_llm_provider", None)

            # Get model info if available
            self.model_info = None
            try:
                self.model_info = litellm.get_model_info(self.model)
            except Exception as e:
                logger.warning(f"Could not get model info for {self.model}: {e}")

            # Configure litellm
            if self.api_type == "azure":
                litellm.api_base = self.base_url
                litellm.api_key = self.api_key
                litellm.api_version = self.api_version
            else:
                litellm.api_key = self.api_key
                if self.base_url:
                    litellm.api_base = self.base_url

            # Initialize cost tracker
            self.cost_tracker = Cost()
            self.initialized = True

            # Initialize completion function
            self._initialize_completion_function()

    def _initialize_completion_function(self):
        """Initialize the completion function with retry logic"""

        def attempt_on_error(retry_state):
            logger.error(
                f"{retry_state.outcome.exception()}. Attempt #{retry_state.attempt_number}"
            )
            return True

        @retry(
            reraise=True,
            stop=stop_after_attempt(self.num_retries),
            wait=wait_random_exponential(
                min=self.retry_min_wait, max=self.retry_max_wait
            ),
            retry=retry_if_exception_type(
                (RateLimitError, APIConnectionError, ServiceUnavailableError)
            ),
            after=attempt_on_error,
        )
        def wrapper(*args, **kwargs):
            model_name = self.model
            if self.api_type == "azure":
                model_name = f"azure/{self.model}"

            # Set default parameters if not provided
            if "max_tokens" not in kwargs:
                kwargs["max_tokens"] = self.max_tokens
            if "temperature" not in kwargs:
                kwargs["temperature"] = self.temperature
            if "top_p" not in kwargs:
                kwargs["top_p"] = self.top_p
            if "timeout" not in kwargs:
                kwargs["timeout"] = self.timeout

            kwargs["model"] = model_name

            # Add API credentials if not in kwargs
            if "api_key" not in kwargs:
                kwargs["api_key"] = self.api_key
            if "base_url" not in kwargs and self.base_url:
                kwargs["base_url"] = self.base_url
            if "api_version" not in kwargs and self.api_version:
                kwargs["api_version"] = self.api_version
            if "custom_llm_provider" not in kwargs and self.custom_llm_provider:
                kwargs["custom_llm_provider"] = self.custom_llm_provider

            resp = completion(**kwargs)
            return resp

        self._completion = wrapper

    @staticmethod
    def format_messages(messages: List[Union[dict, Message]]) -> List[dict]:
        """
        Format messages for LLM by converting them to OpenAI message format.

        Args:
            messages: List of messages that can be either dict or Message objects

        Returns:
            List[dict]: List of formatted messages in OpenAI format

        Raises:
            ValueError: If messages are invalid or missing required fields
            TypeError: If unsupported message types are provided
        """
        formatted_messages = []

        for message in messages:
            if isinstance(message, dict):
                # If message is already a dict, ensure it has required fields
                if "role" not in message:
                    raise ValueError("Message dict must contain 'role' field")
                formatted_messages.append(message)
            elif isinstance(message, Message):
                # If message is a Message object, convert it to dict
                formatted_messages.append(message.to_dict())
            else:
                raise TypeError(f"Unsupported message type: {type(message)}")

        # Validate all messages have required fields
        for msg in formatted_messages:
            if msg["role"] not in ["system", "user", "assistant", "tool"]:
                raise ValueError(f"Invalid role: {msg['role']}")
            if "content" not in msg and "tool_calls" not in msg:
                raise ValueError(
                    "Message must contain either 'content' or 'tool_calls'"
                )

        return formatted_messages

    def _calculate_and_track_cost(self, response) -> float:
        """
        Calculate and track the cost of an LLM API call.

        Args:
            response: The response from litellm

        Returns:
            float: The calculated cost
        """
        try:
            # Use litellm's completion_cost function
            cost = completion_cost(completion_response=response)

            # Add the cost to our tracker
            if cost > 0:
                self.cost_tracker.add_cost(cost)
                logger.info(
                    f"Added cost: ${cost:.6f}, Total: ${self.cost_tracker.accumulated_cost:.6f}"
                )

            return cost
        except Exception as e:
            logger.warning(f"Cost calculation failed: {e}")
            return 0.0

    def is_local(self) -> bool:
        """
        Check if the model is running locally.

        Returns:
            bool: True if the model is running locally, False otherwise
        """
        if self.base_url:
            return any(
                substring in self.base_url
                for substring in ["localhost", "127.0.0.1", "0.0.0.0"]
            )
        if self.model and (
            self.model.startswith("ollama") or "local" in self.model.lower()
        ):
            return True
        return False

    def do_completion(self, *args, **kwargs) -> Tuple[Any, float, float]:
        """
        Perform a completion request and track cost.

        Returns:
            Tuple[Any, float, float]: (response, current_cost, accumulated_cost)
        """
        response = self._completion(*args, **kwargs)

        # Calculate and track cost
        current_cost = self._calculate_and_track_cost(response)

        return response, current_cost, self.cost_tracker.accumulated_cost

    @staticmethod
    def encode_image(image_path: str) -> str:
        """
        Encode an image to base64.

        Args:
            image_path: Path to the image file

        Returns:
            str: Base64-encoded image
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def prepare_messages(
        self, text: str, image_path: Optional[str] = None
    ) -> List[dict]:
        """
        Prepare messages for completion, including multimodal content if needed.

        Args:
            text: Text content
            image_path: Optional path to an image file

        Returns:
            List[dict]: Formatted messages
        """
        messages = [{"role": "user", "content": text}]
        if image_path:
            base64_image = self.encode_image(image_path)
            messages[0]["content"] = [
                {"type": "text", "text": text},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ]
        return messages

    def do_multimodal_completion(
        self, text: str, image_path: str
    ) -> Tuple[Any, float, float]:
        """
        Perform a multimodal completion with text and image.

        Args:
            text: Text prompt
            image_path: Path to the image file

        Returns:
            Tuple[Any, float, float]: (response, current_cost, accumulated_cost)
        """
        messages = self.prepare_messages(text, image_path=image_path)
        return self.do_completion(messages=messages)

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
    )
    async def ask(
        self,
        messages: List[Union[dict, Message]],
        system_msgs: Optional[List[Union[dict, Message]]] = None,
        stream: bool = True,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Send a prompt to the LLM and get the response.

        Args:
            messages: List of conversation messages
            system_msgs: Optional system messages to prepend
            stream (bool): Whether to stream the response
            temperature (float): Sampling temperature for the response

        Returns:
            str: The generated response

        Raises:
            ValueError: If messages are invalid or response is empty
            Exception: For unexpected errors
        """
        try:
            # Format system and user messages
            if system_msgs:
                system_msgs = self.format_messages(system_msgs)
                messages = system_msgs + self.format_messages(messages)
            else:
                messages = self.format_messages(messages)

            model_name = self.model
            if self.api_type == "azure":
                # For Azure, litellm expects model name in format: azure/<deployment_name>
                model_name = f"azure/{self.model}"

            if not stream:
                # Non-streaming request
                response = await litellm.acompletion(
                    model=model_name,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=temperature or self.temperature,
                    stream=False,
                )

                # Calculate and track cost
                self._calculate_and_track_cost(response)

                if not response.choices or not response.choices[0].message.content:
                    raise ValueError("Empty or invalid response from LLM")
                return response.choices[0].message.content

            # Streaming request
            collected_messages = []
            async for chunk in await litellm.acompletion(
                model=model_name,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=temperature or self.temperature,
                stream=True,
            ):
                chunk_message = chunk.choices[0].delta.content or ""
                collected_messages.append(chunk_message)
                print(chunk_message, end="", flush=True)

            # For streaming responses, cost is calculated on the last chunk
            if hasattr(chunk, "usage") and chunk.usage:
                self._calculate_and_track_cost(chunk)

            print()  # Newline after streaming
            full_response = "".join(collected_messages).strip()
            if not full_response:
                raise ValueError("Empty response from streaming LLM")
            return full_response

        except ValueError as ve:
            logger.error(f"Validation error: {ve}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in ask: {e}")
            raise

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
    )
    async def ask_tool(
        self,
        messages: List[Union[dict, Message]],
        system_msgs: Optional[List[Union[dict, Message]]] = None,
        timeout: int = 60,
        tools: Optional[List[dict]] = None,
        tool_choice: Literal["none", "auto", "required"] = "auto",
        temperature: Optional[float] = None,
        **kwargs,
    ):
        """
        Ask LLM using functions/tools and return the response.

        Args:
            messages: List of conversation messages
            system_msgs: Optional system messages to prepend
            timeout: Request timeout in seconds
            tools: List of tools to use
            tool_choice: Tool choice strategy
            temperature: Sampling temperature for the response
            **kwargs: Additional completion arguments

        Returns:
            The model's response

        Raises:
            ValueError: If tools, tool_choice, or messages are invalid
            Exception: For unexpected errors
        """
        try:
            # Validate tool_choice
            if tool_choice not in ["none", "auto", "required"]:
                raise ValueError(f"Invalid tool_choice: {tool_choice}")

            # Format messages
            if system_msgs:
                system_msgs = self.format_messages(system_msgs)
                messages = system_msgs + self.format_messages(messages)
            else:
                messages = self.format_messages(messages)

            # Validate tools if provided
            if tools:
                for tool in tools:
                    if not isinstance(tool, dict) or "type" not in tool:
                        raise ValueError("Each tool must be a dict with 'type' field")

            model_name = self.model
            if self.api_type == "azure":
                # For Azure, litellm expects model name in format: azure/<deployment_name>
                model_name = f"azure/{self.model}"

            # Set up the completion request
            response = await litellm.acompletion(
                model=model_name,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=self.max_tokens,
                tools=tools,
                tool_choice=tool_choice,
                timeout=timeout,
                **kwargs,
            )

            # Calculate and track cost
            self._calculate_and_track_cost(response)

            # Check if response is valid
            if not response.choices or not response.choices[0].message:
                print(response)
                raise ValueError("Invalid or empty response from LLM")

            return response.choices[0].message

        except ValueError as ve:
            logger.error(f"Validation error: {ve}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in ask_tool: {e}")
            raise

    def get_cost(self):
        """
        Get the current cost information.

        Returns:
            dict: Dictionary containing accumulated cost and individual costs
        """
        return self.cost_tracker.get()

    def log_cost(self):
        """
        Log the current cost information.

        Returns:
            str: Formatted string of cost information
        """
        return self.cost_tracker.log()

    def get_token_count(self, messages):
        """
        Get the token count for a list of messages.

        Args:
            messages: List of messages

        Returns:
            int: Token count
        """
        return litellm.token_counter(model=self.model, messages=messages)

    def __str__(self):
        return f"LLM(model={self.model}, base_url={self.base_url})"

    def __repr__(self):
        return str(self)


# Example usage
if __name__ == "__main__":
    # Load environment variables if needed
    from dotenv import load_dotenv

    load_dotenv()

    # Create LLM instance
    llm = LLM()

    # Test text completion
    messages = llm.prepare_messages("Hello, how are you?")
    response, cost, total_cost = llm.do_completion(messages=messages)
    print(f"Response: {response['choices'][0]['message']['content']}")
    print(f"Cost: ${cost:.6f}, Total cost: ${total_cost:.6f}")

    # Test multimodal if image path is available
    image_path = os.getenv("TEST_IMAGE_PATH")
    if image_path and os.path.exists(image_path):
        multimodal_response, mm_cost, mm_total_cost = llm.do_multimodal_completion(
            "What's in this image?", image_path
        )
        print(
            f"Multimodal response: {multimodal_response['choices'][0]['message']['content']}"
        )
        print(f"Cost: ${mm_cost:.6f}, Total cost: ${mm_total_cost:.6f}")

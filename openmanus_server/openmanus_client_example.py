import asyncio
import os
from contextlib import AsyncExitStack
from typing import Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class OpenManusClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.stdio = None
        self.write = None

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server via stdio

        Args:
            server_script_path: Path to the server script
        """
        if not server_script_path.endswith(".py"):
            raise ValueError("Server script must be a .py file")

        # Get the current directory to add to PYTHONPATH
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)  # Get parent directory

        # Prepare environment variables
        env = os.environ.copy()  # Copy current environment

        # Add current directory and project root to PYTHONPATH
        path_separator = (
            ";" if os.name == "nt" else ":"
        )  # Use ; for Windows, : for Unix
        if "PYTHONPATH" in env:
            env[
                "PYTHONPATH"
            ] = f"{current_dir}{path_separator}{project_root}{path_separator}{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = f"{current_dir}{path_separator}{project_root}"

        server_params = StdioServerParameters(
            command="python", args=[server_script_path], env=env
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])
        return tools

    async def run_examples(self):
        """Run example tool calls to demonstrate functionality"""
        try:
            print("\nExample 1: Google Search")
            search_result = await self.session.call_tool(
                "google_search", {"query": "Model Context Protocol", "num_results": 5}
            )
            print(f"Search results: {search_result.content}")

            print("\nExample 2: Python Code Execution")
            code = """
import math
result = 0
for i in range(1, 10):
    result += math.sqrt(i)
print(f"Calculation result: {result}")
"""
            python_result = await self.session.call_tool(
                "python_execute", {"code": code, "timeout": 3}
            )
            print(f"Python execution result: {python_result.content}")

            print("\nExample 3: File Saving")
            file_result = await self.session.call_tool(
                "file_saver",
                {
                    "content": "This is a test file content saved through MCP",
                    "file_path": "mcp_test_file.txt",
                },
            )
            print(f"File save result: {file_result.content}")

            print("\nExample 4: Browser Usage")
            # Navigate to webpage
            browser_result = await self.session.call_tool(
                "browser_use", {"action": "navigate", "url": "https://www.example.com"}
            )
            print(f"Browser navigation result: {browser_result.content}")

            # Get browser state
            state_result = await self.session.call_tool("get_browser_state", {})
            print(f"Browser state: {state_result.content}")

        except Exception as e:
            print(f"\nError during example execution: {str(e)}")

    async def chat_loop(self):
        """Run an interactive chat loop for testing tools"""
        print("\nOpenManus MCP Client Started!")
        print("Type your commands or 'quit' to exit.")
        print(
            "Available commands: google_search, python_execute, file_saver, browser_use, get_browser_state"
        )

        while True:
            try:
                command = input("\nCommand: ").strip()

                if command.lower() == "quit":
                    break

                # Parse command and parameters
                parts = command.split(maxsplit=1)
                if len(parts) == 0:
                    continue

                tool_name = parts[0]
                tool_args = {}
                if len(parts) > 1:
                    try:
                        tool_args = eval(parts[1])  # Convert string to dict
                    except:
                        print(
                            "Invalid arguments format. Please provide a valid Python dictionary."
                        )
                        continue

                result = await self.session.call_tool(tool_name, tool_args)
                print("\nResult:", result.content)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
        await self.exit_stack.aclose()
        print("\nClosed MCP client connection")


async def main():
    """Main entry point"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python openmanus_client_example.py <path_to_server_script>")
        print("Example: python openmanus_client_example.py ../mcp_server.py")
        sys.exit(1)

    client = OpenManusClient()
    try:
        await client.connect_to_server(server_script_path=sys.argv[1])

        # Run examples first
        await client.run_examples()

        # Then start interactive chat loop
        await client.chat_loop()

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

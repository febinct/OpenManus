from typing import List

from pydantic import Field

from app.agent.toolcall import ToolCallAgent
from app.prompt.swe import NEXT_STEP_TEMPLATE, SYSTEM_PROMPT
from app.tool import AiderTool, Bash, StrReplaceEditor, Terminate, ToolCollection
from app.tool.code_editor import FileEditor


class SWEAgent(ToolCallAgent):
    """An agent that implements the SWEAgent paradigm for executing code and natural conversations."""

    name: str = "swe"
    description: str = "an autonomous AI programmer that interacts directly with the computer to solve tasks."

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_TEMPLATE

    available_tools: ToolCollection = ToolCollection(
        Bash(), StrReplaceEditor(), AiderTool(), Terminate(),FileEditor(), # Add FileEditor() to the list

    )
    special_tool_names: List[str] = Field(default_factory=lambda: [Terminate().name])

    max_steps: int = 30

    bash: Bash = Field(default_factory=Bash)
    working_dir: str = "."

    async def think(self) -> bool:
        """Process current state and decide next action"""
        # Update working directory
        self.working_dir = await self.bash.execute("pwd")
        self.next_step_prompt = self.next_step_prompt.format(
            current_dir=self.working_dir
        )

        return await super().think()

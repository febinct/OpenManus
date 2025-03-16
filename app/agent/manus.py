import asyncio
from typing import Any, List

from pydantic import Field

from app.agent.toolcall import ToolCallAgent
from app.logger import logger
from app.prompt.manus import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import Terminate, ToolCollection
from app.tool.ask_human import AskHuman
from app.tool.browser_use_tool import BrowserUseTool
from app.tool.code_editor import FileEditor  # Using FileEditor from code_editor.py
from app.tool.python_execute import PythonExecute
from app.tool.repo_map import RepoMapTool
from app.tool.web_search import WebSearch


class Manus(ToolCallAgent):
    """
    A versatile general-purpose agent that uses planning to solve various tasks.

    This agent extends PlanningAgent with a comprehensive set of tools and capabilities,
    including Python execution, web browsing, file operations, and information retrieval
    to handle a wide range of user requests.
    """

    name: str = "Manus"
    description: str = (
        "A versatile agent that can solve various tasks using multiple tools"
    )

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 2000
    max_steps: int = 20

    # Add general-purpose tools to the tool collection
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            PythonExecute(), WebSearch(), BrowserUseTool(),
            FileEditor(), AskHuman(), Terminate()
        )
    )

    # Track current edit mode
    current_edit_mode: str = "diff"  # Default to diff mode

    async def set_edit_mode(self, mode: str) -> str:
        """Set the current file editing mode"""
        valid_modes = ["whole", "diff", "udiff"]
        if mode not in valid_modes:
            return f"Invalid edit mode: {mode}. Valid modes are: {', '.join(valid_modes)}"

        self.current_edit_mode = mode
        logger.info(f"File edit mode set to: {mode}")
        return f"Edit mode set to: {mode}"

    async def _handle_special_tool(self, name: str, result: Any, **kwargs):
        if not self._is_special_tool(name):
            return
        else:
            await self.available_tools.get_tool(BrowserUseTool().name).cleanup()
            await super()._handle_special_tool(name, result, **kwargs)

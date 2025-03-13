import asyncio
from typing import Any, Dict, List

from pydantic import Field

from app.agent.toolcall import ToolCallAgent
from app.logger import logger
from app.mcp.tool import MCPTool, MCPToolRegistry
from app.prompt.manus import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import Terminate, ToolCollection
from app.tool.browser_use_tool import BrowserUseTool
from app.tool.file_saver import FileSaver
from app.tool.web_search import WebSearch
from app.tool.python_execute import PythonExecute
from app.config import config


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
            PythonExecute(), WebSearch(), BrowserUseTool(), FileSaver(), Terminate()
        )
    )
    
    # MCP tools that have been registered
    mcp_tools: Dict[str, MCPTool] = Field(default_factory=dict)
    
    async def initialize(self):
        """Initialize the agent, including MCP tools."""
        try:
            # Check if MCP module is available
            from app.mcp.tool import MCPToolRegistry, HAS_MCP_SDK
            
            if HAS_MCP_SDK:
                # Initialize MCP tools
                self.mcp_tools = await MCPToolRegistry.initialize()
                
                # Add MCP tools to available tools
                for tool_name, tool in self.mcp_tools.items():
                    self.available_tools.add_tool(tool)
                
                # Update next_step_prompt to include MCP tools
                if self.mcp_tools:
                    mcp_tools_desc = "\n\n".join([
                        f"{tool.name}: {tool.description} Parameters: {tool.parameters}"
                        for tool in self.mcp_tools.values()
                    ])
                    
                    # Add MCP tools to the prompt
                    from app.prompt.manus import NEXT_STEP_PROMPT
                    tools_intro = "You can interact with the computer using PythonExecute"
                    mcp_tools_intro = f"You can interact with the computer using PythonExecute and MCP tools like {', '.join(self.mcp_tools.keys())}"
                    
                    # Update the prompt
                    self.next_step_prompt = NEXT_STEP_PROMPT.replace(
                        tools_intro, mcp_tools_intro
                    ) + f"\n\n{mcp_tools_desc}"
                    
                logger.info(f"Initialized {len(self.mcp_tools)} MCP tools")
            else:
                logger.info("MCP SDK not installed. MCP tools will not be available.")
                self.mcp_tools = {}
        except ImportError:
            logger.info("MCP module not available. MCP tools will not be used.")
            self.mcp_tools = {}
        except Exception as e:
            logger.error(f"Failed to initialize MCP tools: {e}")
            self.mcp_tools = {}

    async def _handle_special_tool(self, name: str, result: Any, **kwargs):
        # Clean up browser tool
        await self.available_tools.get_tool(BrowserUseTool().name).cleanup()
        
        # Clean up MCP tools if terminating
        if name == "terminate":
            try:
                from app.mcp.client import mcp_client
                try:
                    await mcp_client.stop_servers()
                except Exception as e:
                    logger.error(f"Error stopping MCP servers: {e}")
            except ImportError:
                pass
        
        await super()._handle_special_tool(name, result, **kwargs)
        
    @classmethod
    async def create(cls, **kwargs):
        """Create and initialize a new Manus agent."""
        agent = cls(**kwargs)
        await agent.initialize()
        return agent

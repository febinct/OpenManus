"""MCP tool adapter for OpenManus."""
import json
from typing import Any, Dict, Optional

from pydantic import Field

from app.logger import logger
from app.mcp.client import mcp_client, HAS_MCP_SDK, MCPToolResponse
from app.tool.base import BaseTool, ToolResult


class MCPTool(BaseTool):
    """Tool that calls an MCP server tool."""
    
    server_name: str = ""
    tool_name: str = ""
    
    def __init__(
        self,
        server_name: str,
        tool_name: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        """Initialize an MCP tool.
        
        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool on the MCP server
            name: Name of the tool in OpenManus (defaults to server_name.tool_name)
            description: Description of the tool (defaults to the MCP tool description)
            parameters: Parameters schema (defaults to the MCP tool input schema)
        """
        if not HAS_MCP_SDK:
            raise ImportError("MCP SDK not installed. Cannot create MCP tool.")
            
        # Find the tool in the server
        server = mcp_client.servers.get(server_name)
        if not server:
            raise ValueError(f"MCP server {server_name} not found")
        
        mcp_tool = next((t for t in server.tools if t.name == tool_name), None)
        if not mcp_tool:
            raise ValueError(f"MCP tool {tool_name} not found on server {server_name}")
        
        # Use provided values or defaults from MCP tool
        # Ensure tool name follows the pattern ^[a-zA-Z0-9_-]{1,64}$
        if name is None:
            # Replace dots with underscores to follow naming pattern
            name = f"{server_name}_{tool_name}"
            
        # Validate name format
        import re
        if not re.match(r'^[a-zA-Z0-9_-]{1,64}$', name):
            # Sanitize name to follow the pattern
            name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)[:64]
            
        description = description or mcp_tool.description
        
        # Ensure parameters have the correct format
        if parameters is None:
            # Get input schema from MCP tool
            input_schema = mcp_tool.inputSchema
            
            # Ensure input schema has 'type' field
            if isinstance(input_schema, dict) and 'type' not in input_schema:
                input_schema = {
                    "type": "object",
                    "properties": input_schema.get("properties", {}),
                    "required": input_schema.get("required", [])
                }
            
            parameters = input_schema
        
        super().__init__(
            name=name,
            description=description,
            parameters=parameters,
        )
        
        # Set server and tool names after initialization
        self.server_name = server_name
        self.tool_name = tool_name
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the MCP tool."""
        try:
            logger.info(f"Executing MCP tool {self.server_name}.{self.tool_name}")
            response = await mcp_client.call_tool(
                server_name=self.server_name,
                tool_name=self.tool_name,
                arguments=kwargs,
            )
            
            if response.success:
                # Try to parse JSON if the result is a string
                if isinstance(response.content, str):
                    try:
                        parsed_result = json.loads(response.content)
                        return ToolResult(output=parsed_result)
                    except json.JSONDecodeError:
                        pass
                
                return ToolResult(output=response.content)
            else:
                return ToolResult(error=response.error)
        except Exception as e:
            logger.error(f"Error executing MCP tool {self.name}: {e}")
            return ToolResult(error=f"Error executing MCP tool: {str(e)}")


class MCPToolRegistry:
    """Registry for MCP tools."""
    
    @staticmethod
    async def initialize() -> Dict[str, MCPTool]:
        """Initialize MCP tools from all servers."""
        if not HAS_MCP_SDK:
            logger.warning("MCP SDK not installed. MCP tools will not be available.")
            return {}
            
        # Make sure MCP client is initialized
        await mcp_client.initialize()
        
        tools = {}
        
        # Create tools for each server
        for server_name, server in mcp_client.servers.items():
            for mcp_tool in server.tools:
                try:
                    tool = MCPTool(
                        server_name=server_name,
                        tool_name=mcp_tool.name,
                    )
                    tools[tool.name] = tool
                    logger.info(f"Registered MCP tool: {tool.name}")
                except Exception as e:
                    logger.error(f"Failed to register MCP tool {mcp_tool.name}: {e}")
        
        return tools

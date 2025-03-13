"""MCP client for connecting to MCP servers."""
import asyncio
import json
import logging
import os
import subprocess
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, model_validator

from app.logger import logger

# Import MCP SDK
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp import types as mcp_types
    HAS_MCP_SDK = True
except ImportError:
    logger.warning("MCP SDK not installed. MCP tools will not be available.")
    HAS_MCP_SDK = False


class MCPToolSchema(BaseModel):
    """Schema for an MCP tool."""
    name: str
    description: str
    inputSchema: Dict[str, Any]


class MCPToolResponse(BaseModel):
    """Response from an MCP tool call."""
    success: bool
    content: Optional[Union[str, Dict[str, Any]]] = None
    error: Optional[str] = None
    
    @model_validator(mode='after')
    def check_content_or_error(self) -> 'MCPToolResponse':
        """Ensure either content or error is provided based on success."""
        if self.success and not self.content:
            self.content = "Tool executed successfully with no content"
        elif not self.success and not self.error:
            self.error = "Unknown error occurred"
            
        return self


class MCPServer(BaseModel):
    """Configuration for an MCP server."""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str] = Field(default_factory=dict)
    disabled: bool = False
    autoApprove: List[str] = Field(default_factory=list)
    
    process: Optional[subprocess.Popen] = None
    tools: List[MCPToolSchema] = Field(default_factory=list)
    client: Optional[Any] = None
    
    class Config:
        arbitrary_types_allowed = True


class MCPClient:
    """Client for interacting with MCP servers."""
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MCPClient, cls).__new__(cls)
            cls._instance.servers = {}
            cls._instance.initialized = False
            cls._instance.exit_stack = AsyncExitStack()
            cls._instance.session = None
        return cls._instance
    
    def __init__(self):
        # Initialization is done in __new__ to ensure it only happens once
        pass
    
    async def initialize(self, config_path: Optional[str] = None):
        """Initialize MCP client from config file."""
        if self.initialized or not HAS_MCP_SDK:
            return
        
        # Default config paths
        if config_path is None:
            home_dir = os.path.expanduser("~")
            possible_paths = [
                os.path.join(home_dir, ".config", "openmanus", "mcp_config.json"),
                os.path.join(home_dir, "Library", "Application Support", "OpenManus", "mcp_config.json"),
                os.path.join("config", "mcp_config.json"),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                
                for server_name, server_config in config.get("mcpServers", {}).items():
                    if server_config.get("disabled", False):
                        continue
                    
                    # Get auto-approve list with security validation
                    auto_approve = server_config.get("autoApprove", [])
                    
                    # Security check: Warn about potentially dangerous auto-approved tools
                    if auto_approve:
                        dangerous_patterns = [
                            "exec", "eval", "system", "popen", "subprocess", 
                            "shell", "command", "run", "script", "code"
                        ]
                        for tool in auto_approve:
                            if any(pattern in tool.lower() for pattern in dangerous_patterns):
                                logger.warning(
                                    f"SECURITY WARNING: Tool '{tool}' in server '{server_name}' "
                                    f"is auto-approved but matches a potentially dangerous pattern. "
                                    f"Auto-approving tools that execute code can be a security risk."
                                )
                    
                    server = MCPServer(
                        name=server_name,
                        command=server_config["command"],
                        args=server_config.get("args", []),
                        env=server_config.get("env", {}),
                        disabled=server_config.get("disabled", False),
                        autoApprove=auto_approve,
                    )
                    
                    self.servers[server_name] = server
            except Exception as e:
                logger.error(f"Failed to load MCP config: {e}")
        
        # Create MCP session - we don't need to create a session here
        # as we'll use stdio_client directly which handles session creation
        self.session = None
        
        # Start servers
        await self.start_servers()
        
        self.initialized = True
    
    async def start_servers(self):
        """Start all configured MCP servers."""
        if not HAS_MCP_SDK:
            return
            
        for server_name, server in self.servers.items():
            if server.disabled:
                continue
            
            try:
                # Start server process with MCP SDK
                env = os.environ.copy()
                env.update(server.env)
                
                # Create server parameters
                params = StdioServerParameters(
                    command=server.command,
                    args=server.args,
                    env=env,
                )
                
                # Connect to server
                try:
                    # Connect using stdio transport
                    stdio_transport = await self.exit_stack.enter_async_context(
                        stdio_client(params)
                    )
                    
                    # Create session from transport
                    read_stream, write_stream = stdio_transport
                    session = await self.exit_stack.enter_async_context(
                        ClientSession(read_stream, write_stream)
                    )
                    
                    # Initialize session
                    await session.initialize()
                    server.client = session
                    
                    # Get available tools
                    await self.fetch_server_tools(server_name)
                    
                    logger.info(f"Started MCP server: {server_name}")
                except Exception as e:
                    logger.error(f"Failed to connect to MCP server {server_name}: {e}")
            except Exception as e:
                logger.error(f"Failed to start MCP server {server_name}: {e}")
    
    async def stop_servers(self):
        """Stop all running MCP servers."""
        if not HAS_MCP_SDK:
            return
        
        try:
            # Close each server client individually first
            for server_name, server in self.servers.items():
                if server.client:
                    try:
                        # Try to close the client gracefully
                        if hasattr(server.client, 'close'):
                            await server.client.close()
                        server.client = None
                    except Exception as e:
                        logger.error(f"Error closing MCP server {server_name}: {e}")
            
            # Then close the exit stack
            try:
                await self.exit_stack.aclose()
            except RuntimeError as e:
                if "Attempted to exit cancel scope in a different task" in str(e):
                    logger.warning("Ignoring cancel scope error during shutdown")
                else:
                    raise
        except Exception as e:
            logger.error(f"Error stopping MCP servers: {e}")
        
        self.initialized = False
    
    async def fetch_server_tools(self, server_name: str) -> List[MCPToolSchema]:
        """Fetch available tools from an MCP server."""
        if not HAS_MCP_SDK:
            return []
            
        server = self.servers.get(server_name)
        if not server or not server.client:
            logger.error(f"MCP server {server_name} not found or not running")
            return []
        
        try:
            # Get tools from server
            tools_response = await server.client.list_tools()
            
            # Log basic info about tools response at debug level
            logger.debug(f"Received tools response from {server_name}")
            
            # Handle different response formats
            tools = []
            
            # Check if tools_response is a tuple (client, response) from FastMCP
            if isinstance(tools_response, tuple) and len(tools_response) == 2:
                # FastMCP returns (client, response)
                _, response = tools_response
                if hasattr(response, 'tools'):
                    tool_list = response.tools
                else:
                    # Try to access tools from response.result
                    tool_list = getattr(response, 'result', {}).get('tools', [])
            elif hasattr(tools_response, 'tools'):
                # Direct response with tools attribute
                tool_list = tools_response.tools
            else:
                # Try to access tools from dictionary
                tool_list = getattr(tools_response, 'result', {}).get('tools', [])
            
            # Convert to MCPToolSchema
            for tool in tool_list:
                # Handle different tool formats
                if hasattr(tool, 'name'):
                    # Object with attributes
                    name = tool.name
                    description = getattr(tool, 'description', '') or ''
                    input_schema = getattr(tool, 'input_schema', {}) or {}
                    
                    # Ensure input schema has 'type' field
                    if isinstance(input_schema, dict) and 'type' not in input_schema:
                        input_schema = {
                            "type": "object",
                            "properties": input_schema.get("properties", {}),
                            "required": input_schema.get("required", [])
                        }
                elif isinstance(tool, dict):
                    # Dictionary format
                    name = tool.get('name', '')
                    description = tool.get('description', '')
                    input_schema = tool.get('inputSchema', {}) or tool.get('input_schema', {})
                    
                    # Ensure input schema has 'type' field
                    if isinstance(input_schema, dict) and 'type' not in input_schema:
                        input_schema = {
                            "type": "object",
                            "properties": input_schema.get("properties", {}),
                            "required": input_schema.get("required", [])
                        }
                else:
                    # Skip invalid tool format
                    continue
                
                tools.append(MCPToolSchema(
                    name=name,
                    description=description,
                    inputSchema=input_schema,
                ))
            
            server.tools = tools
            return tools
        except Exception as e:
            logger.error(f"Failed to fetch tools from MCP server {server_name}: {e}")
        
        return []
    
    async def call_tool(
        self, server_name: str, tool_name: str, arguments: Dict[str, Any]
    ) -> MCPToolResponse:
        """Call a tool on an MCP server.
        
        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            MCPToolResponse: Response from the tool call with success status and content/error
        """
        if not HAS_MCP_SDK:
            return MCPToolResponse(success=False, error="MCP SDK not installed")
            
        server = self.servers.get(server_name)
        if not server or not server.client:
            return MCPToolResponse(
                success=False, 
                error=f"MCP server {server_name} not found or not running"
            )
        
        try:
            # Call tool directly on the session
            logger.info(f"Executing MCP tool {server_name}.{tool_name}")
            result = await server.client.call_tool(tool_name, arguments)
            
            # Process result
            if hasattr(result, 'is_error') and result.is_error:
                return MCPToolResponse(
                    success=False,
                    error=f"MCP error: {getattr(result, 'error_message', 'Unknown error')}"
                )
            
            # Handle string result (FastMCP often returns strings directly)
            if isinstance(result, str):
                return MCPToolResponse(success=True, content=result)
            
            # Extract text content if available
            if hasattr(result, 'content') and result.content and len(result.content) > 0:
                for content in result.content:
                    if isinstance(content, mcp_types.TextContent):
                        return MCPToolResponse(success=True, content=content.text)
                
                # Return raw content if no text content found
                return MCPToolResponse(success=True, content=result.content)
            
            return MCPToolResponse(success=True)
        except Exception as e:
            error_msg = f"Failed to call tool {tool_name} on MCP server {server_name}: {e}"
            logger.error(error_msg)
            return MCPToolResponse(success=False, error=error_msg)


# Singleton instance
mcp_client = MCPClient()

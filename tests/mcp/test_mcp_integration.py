"""Tests for MCP integration."""
import asyncio
import json
import os
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.mcp.client import MCPClient, MCPServer, MCPToolResponse, MCPToolSchema
from app.mcp.tool import MCPTool, MCPToolRegistry
from app.tool.base import ToolResult


def async_test(coro):
    """Decorator for async test methods."""
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))
    return wrapper


class TestMCPClient(unittest.TestCase):
    """Test the MCP client."""

    def setUp(self):
        """Set up the test."""
        # Reset the singleton instance
        MCPClient._instance = None
        self.client = MCPClient()
        self.client.servers = {}
        self.client.initialized = False

    @async_test
    @patch('app.mcp.client.HAS_MCP_SDK', True)
    async def test_initialize(self):
        """Test initializing the MCP client."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump({
                "mcpServers": {
                    "test-server": {
                        "command": "python",
                        "args": ["-m", "test_server"],
                        "env": {"TEST_ENV": "test-value"},
                        "disabled": False,
                        "autoApprove": ["test-tool"]
                    }
                }
            }, f)
            config_path = f.name

        try:
            # Mock the start_servers method to do nothing
            self.client.start_servers = AsyncMock()
            
            # Initialize the client
            await self.client.initialize(config_path)
            
            # Check that the server was added
            self.assertIn("test-server", self.client.servers)
            server = self.client.servers["test-server"]
            self.assertEqual(server.name, "test-server")
            self.assertEqual(server.command, "python")
            self.assertEqual(server.args, ["-m", "test_server"])
            self.assertEqual(server.env, {"TEST_ENV": "test-value"})
            self.assertEqual(server.autoApprove, ["test-tool"])
            
            # Check that the server was started
            self.assertTrue(self.client.initialized)
            self.client.start_servers.assert_called_once()
        finally:
            # Clean up
            os.unlink(config_path)

    @async_test
    @patch('app.mcp.client.HAS_MCP_SDK', True)
    async def test_call_tool(self):
        """Test calling a tool."""
        # Create a mock server
        server = MCPServer(
            name="test-server",
            command="python",
            args=["-m", "test_server"],
            env={},
            disabled=False,
            autoApprove=["test-tool"],
        )
        server.client = AsyncMock()
        
        # Mock the call_tool method
        server.client.call_tool = AsyncMock(return_value="test-result")
        
        # Add the server to the client
        self.client.servers["test-server"] = server
        
        # Call the tool
        result = await self.client.call_tool("test-server", "test-tool", {"arg": "value"})
        
        # Check the result
        self.assertTrue(result.success)
        self.assertEqual(result.content, "test-result")
        
        # Check that the tool was called
        server.client.call_tool.assert_called_once_with("test-tool", {"arg": "value"})

    @async_test
    @patch('app.mcp.client.HAS_MCP_SDK', True)
    async def test_call_tool_error(self):
        """Test calling a tool that returns an error."""
        # Create a mock server
        server = MCPServer(
            name="test-server",
            command="python",
            args=["-m", "test_server"],
            env={},
            disabled=False,
            autoApprove=["test-tool"],
        )
        server.client = AsyncMock()
        
        # Create a mock error response
        error_response = MagicMock()
        error_response.is_error = True
        error_response.error_message = "test-error"
        
        # Mock the call_tool method
        server.client.call_tool = AsyncMock(return_value=error_response)
        
        # Add the server to the client
        self.client.servers["test-server"] = server
        
        # Call the tool
        result = await self.client.call_tool("test-server", "test-tool", {"arg": "value"})
        
        # Check the result
        self.assertFalse(result.success)
        self.assertEqual(result.error, "MCP error: test-error")
        
        # Check that the tool was called
        server.client.call_tool.assert_called_once_with("test-tool", {"arg": "value"})


class TestMCPTool(unittest.TestCase):
    """Test the MCP tool."""

    @patch('app.mcp.tool.HAS_MCP_SDK', True)
    @patch('app.mcp.tool.mcp_client')
    def test_init(self, mock_client):
        """Test initializing an MCP tool."""
        # Create a mock server
        server = MCPServer(
            name="test-server",
            command="python",
            args=["-m", "test_server"],
            env={},
            disabled=False,
            autoApprove=["test-tool"],
        )
        
        # Create a mock tool schema
        tool_schema = MCPToolSchema(
            name="test-tool",
            description="A test tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "arg": {
                        "type": "string"
                    }
                },
                "required": ["arg"]
            }
        )
        
        # Add the tool to the server
        server.tools = [tool_schema]
        
        # Add the server to the client
        mock_client.servers = {"test-server": server}
        
        # Create the tool
        tool = MCPTool(
            server_name="test-server",
            tool_name="test-tool",
        )
        
        # Check the tool
        self.assertEqual(tool.name, "test-server_test-tool")
        self.assertEqual(tool.description, "A test tool")
        self.assertEqual(tool.server_name, "test-server")
        self.assertEqual(tool.tool_name, "test-tool")
        self.assertEqual(tool.parameters, {
            "type": "object",
            "properties": {
                "arg": {
                    "type": "string"
                }
            },
            "required": ["arg"]
        })

    @async_test
    @patch('app.mcp.tool.HAS_MCP_SDK', True)
    @patch('app.mcp.tool.mcp_client')
    async def test_execute(self, mock_client):
        """Test executing an MCP tool."""
        # Create a mock server
        server = MCPServer(
            name="test-server",
            command="python",
            args=["-m", "test_server"],
            env={},
            disabled=False,
            autoApprove=["test-tool"],
        )
        
        # Create a mock tool schema
        tool_schema = MCPToolSchema(
            name="test-tool",
            description="A test tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "arg": {
                        "type": "string"
                    }
                },
                "required": ["arg"]
            }
        )
        
        # Add the tool to the server
        server.tools = [tool_schema]
        
        # Add the server to the client
        mock_client.servers = {"test-server": server}
        
        # Create the tool
        tool = MCPTool(
            server_name="test-server",
            tool_name="test-tool",
        )
        
        # Mock the call_tool method
        mock_client.call_tool = AsyncMock(
            return_value=MCPToolResponse(success=True, content="test-result")
        )
        
        # Execute the tool
        result = await tool.execute(arg="value")
        
        # Check the result
        self.assertEqual(result.output, "test-result")
        
        # Check that the tool was called
        mock_client.call_tool.assert_called_once_with(
            server_name="test-server",
            tool_name="test-tool",
            arguments={"arg": "value"}
        )

    @async_test
    @patch('app.mcp.tool.HAS_MCP_SDK', True)
    @patch('app.mcp.tool.mcp_client')
    async def test_execute_error(self, mock_client):
        """Test executing an MCP tool that returns an error."""
        # Create a mock server
        server = MCPServer(
            name="test-server",
            command="python",
            args=["-m", "test_server"],
            env={},
            disabled=False,
            autoApprove=["test-tool"],
        )
        
        # Create a mock tool schema
        tool_schema = MCPToolSchema(
            name="test-tool",
            description="A test tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "arg": {
                        "type": "string"
                    }
                },
                "required": ["arg"]
            }
        )
        
        # Add the tool to the server
        server.tools = [tool_schema]
        
        # Add the server to the client
        mock_client.servers = {"test-server": server}
        
        # Create the tool
        tool = MCPTool(
            server_name="test-server",
            tool_name="test-tool",
        )
        
        # Mock the call_tool method
        mock_client.call_tool = AsyncMock(
            return_value=MCPToolResponse(success=False, error="test-error")
        )
        
        # Execute the tool
        result = await tool.execute(arg="value")
        
        # Check the result
        self.assertEqual(result.error, "test-error")
        
        # Check that the tool was called
        mock_client.call_tool.assert_called_once_with(
            server_name="test-server",
            tool_name="test-tool",
            arguments={"arg": "value"}
        )


if __name__ == "__main__":
    unittest.main()

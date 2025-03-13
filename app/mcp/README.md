# MCP Integration for OpenManus

This module provides integration with the Model Context Protocol (MCP) for OpenManus, allowing you to register custom tools from MCP servers.

## Overview

The MCP integration allows OpenManus to:

1. Connect to MCP servers
2. Discover available tools
3. Register tools with the OpenManus agent
4. Execute tools as part of the agent's workflow

## Configuration

MCP servers are configured in a JSON file. By default, the system looks for configuration in the following locations:

- `~/.config/openmanus/mcp_config.json`
- `~/Library/Application Support/OpenManus/mcp_config.json`
- `config/mcp_config.json`

The configuration file should have the following structure:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "command-to-run-server",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR1": "value1",
        "ENV_VAR2": "value2"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Configuration Options

- `command`: The command to run the MCP server
- `args`: Arguments to pass to the command
- `env`: Environment variables to set when running the server
- `disabled`: Whether the server is disabled (default: false)
- `autoApprove`: List of tool names that can be auto-approved (default: empty)

## Creating an MCP Server

You can create an MCP server using the MCP SDK. Here's a simple example using FastMCP with lifespan support:

```python
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from mcp.server.fastmcp import FastMCP

# Define server context
@dataclass
class AppContext:
    """Context for server operations."""
    request_count: int = 0

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context."""
    try:
        # Initialize on startup
        print("Initializing server...")
        context = AppContext()
        yield context
    finally:
        # Cleanup on shutdown
        print(f"Shutting down server. Total requests: {context.request_count}")

# Create a named server with lifespan
app = FastMCP("example-server", lifespan=app_lifespan)

# Define a tool that uses the context
@app.tool()
async def hello_world(ctx, name: str) -> str:
    """Say hello to someone.
    
    Args:
        ctx: Tool context
        name: Name to greet
        
    Returns:
        Greeting message
    """
    # Get lifespan context and increment request count
    app_context = ctx.request_context.lifespan_context
    app_context.request_count += 1
    
    return f"Hello, {name}!"

if __name__ == "__main__":
    app.run(transport="stdio")
```

Save this as `example_server.py` and add it to your MCP configuration:

```json
{
  "mcpServers": {
    "example": {
      "command": "python",
      "args": ["path/to/example_server.py"]
    }
  }
}
```

## Usage

The MCP integration is automatically initialized when the OpenManus agent is created. The agent will connect to all configured MCP servers and register their tools.

You can then use the MCP tools just like any other tool in OpenManus.

### Example: Using MCP Tools in a Prompt

When MCP tools are registered, they are automatically added to the agent's available tools. You can use them in your prompts like this:

```
You can use the calculator_calculate tool to perform calculations.
For example: calculator_calculate(a=5, b=3, operation="add")
```

### Example: Programmatically Using MCP Tools

You can also use MCP tools programmatically:

```python
from app.agent.manus import Manus

# Create and initialize the agent
agent = await Manus.create()

# Use an MCP tool
result = await agent.available_tools.execute(
    name="calculator_calculate",
    tool_input={
        "a": 5,
        "b": 3,
        "operation": "add"
    }
)

print(result)  # Output: Result of 5 add 3 = 8
```

## Advanced Usage

### Auto-Approval of Tools

You can configure certain tools to be auto-approved in the MCP configuration:

```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": ["examples/mcp_server_example.py"],
      "disabled": false,
      "autoApprove": ["calculate", "sqrt"]
    }
  }
}
```

Tools listed in the `autoApprove` array will be executed without requiring user confirmation.

### Custom Tool Names

By default, MCP tools are registered with names in the format `{server_name}_{tool_name}`. You can customize this by providing a custom name when creating an MCPTool:

```python
from app.mcp.tool import MCPTool

custom_tool = MCPTool(
    server_name="calculator",
    tool_name="calculate",
    name="my_custom_calculator"
)
```

## Requirements

- MCP SDK (`pip install mcp`)

## Troubleshooting

### Common Issues

1. **MCP SDK not installed**: If you see the error "MCP SDK not installed", make sure you have installed the MCP SDK with `pip install mcp`.

2. **Server not found**: If you see the error "MCP server X not found", check your MCP configuration file to ensure the server is properly configured.

3. **Tool not found**: If you see the error "MCP tool X not found on server Y", make sure the tool is properly defined in your MCP server.

### Debugging

You can enable debug logging to see more detailed information about MCP operations:

```python
import logging
logging.getLogger("app.mcp").setLevel(logging.DEBUG)
```

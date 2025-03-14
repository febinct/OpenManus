# OpenManus Repository Map

## Project Overview

OpenManus is an autonomous AI agent built as a wrapper around foundation models. It operates in a cloud-based virtual computing environment with access to tools like web browsers, shell commands, and code execution. The system's key innovation is using executable Python code as its action mechanism ("CodeAct" approach), allowing it to perform complex operations autonomously. The architecture consists of an iterative agent loop (analyze → plan → execute → observe), with specialized modules for planning, knowledge retrieval, and memory management.

## Directory Structure

```
OpenManus/
├── app/                       # Main application code
│   ├── agent/                 # Agent implementations
│   │   ├── base.py            # Base agent class
│   │   ├── manus.py           # Main Manus agent implementation
│   │   ├── planning.py        # Planning agent implementation
│   │   ├── react.py           # ReAct agent implementation
│   │   ├── swe.py             # Software engineering agent
│   │   └── toolcall.py        # Tool calling functionality
│   ├── flow/                  # Flow management
│   │   ├── base.py            # Base flow class
│   │   ├── flow_factory.py    # Flow factory
│   │   └── planning.py        # Planning flow
│   ├── llm/                   # LLM integration
│   │   ├── cost.py            # Cost tracking
│   │   └── inference.py       # Inference functionality
│   ├── mcp/                   # MCP SDK integration
│   │   ├── client.py          # MCP client
│   │   └── tool.py            # MCP tool integration
│   ├── prompt/                # System prompts
│   │   ├── code_editor.py     # Code editor prompts
│   │   ├── manus.py           # Manus system prompts
│   │   ├── planning.py        # Planning prompts
│   │   ├── swe.py             # Software engineering prompts
│   │   └── toolcall.py        # Tool calling prompts
│   └── tool/                  # Tool implementations
│       ├── ask_human.py       # Human interaction tool
│       ├── base.py            # Base tool class
│       ├── bash.py            # Bash command execution
│       ├── browser_use_tool.py # Browser interaction
│       ├── code_editor.py     # Code editing tool
│       ├── file_saver.py      # File saving tool
│       ├── python_execute.py  # Python execution tool
│       ├── repo_map.py        # Repository mapping tool
│       ├── search/            # Search tools
│       │   ├── baidu_search.py # Baidu search
│       │   ├── base.py        # Base search class
│       │   ├── duckduckgo_search.py # DuckDuckGo search
│       │   └── google_search.py # Google search
│       ├── terminate.py       # Termination tool
│       ├── tool_collection.py # Tool collection management
│       └── web_search.py      # Web search tool
├── config/                    # Configuration files
├── examples/                  # Example use cases
├── logs/                      # Log files
├── openmanus_server/          # Server implementation
│   ├── openmanus_server.py    # Server code
│   └── openmanus_client.py    # Client code
├── static/                    # Static assets for web UI
├── templates/                 # HTML templates for web UI
├── tests/                     # Test suite
├── app.py                     # FastAPI web application
├── main.py                    # CLI entry point
├── requirements.txt           # Python dependencies
├── run_flow.py                # Flow execution script
└── setup.py                   # Package setup
```

## Key Components

### 1. Agent System

The agent system is built around a modular architecture with different agent implementations:

- **Manus Agent (`app/agent/manus.py`)**: The main agent implementation that combines planning and tool usage to solve complex tasks.
- **ToolCall Agent (`app/agent/toolcall.py`)**: Handles tool calling functionality.
- **ReAct Agent (`app/agent/react.py`)**: Implements the ReAct (Reasoning and Acting) paradigm.
- **Planning Agent (`app/agent/planning.py`)**: Focuses on planning and breaking down complex tasks.

### 2. Tool System

OpenManus provides a rich set of tools for the agent to interact with the environment:

- **Code Editor (`app/tool/code_editor.py`)**: Allows editing code files with different formats (whole file, diff, udiff).
- **Python Execute (`app/tool/python_execute.py`)**: Executes Python code.
- **Browser Tool (`app/tool/browser_use_tool.py`)**: Interacts with web browsers.
- **File Saver (`app/tool/file_saver.py`)**: Saves content to files.
- **Repo Map (`app/tool/repo_map.py`)**: Generates repository structure maps.
- **Web Search (`app/tool/web_search.py`)**: Performs web searches.
- **Ask Human (`app/tool/ask_human.py`)**: Requests human input.
- **Terminate (`app/tool/terminate.py`)**: Ends the interaction.

### 3. Prompt System

The system uses carefully crafted prompts to guide the agent's behavior:

- **Manus Prompts (`app/prompt/manus.py`)**: System and next-step prompts for the Manus agent.
- **Code Editor Prompts (`app/prompt/code_editor.py`)**: Prompts for code editing functionality.
- **Tool Call Prompts (`app/prompt/toolcall.py`)**: Prompts for tool calling.
- **Planning Prompts (`app/prompt/planning.py`)**: Prompts for planning tasks.

### 4. Entry Points

- **CLI (`main.py`)**: Command-line interface for interacting with the agent.
- **Web API (`app.py`)**: FastAPI web application for interacting with the agent through a web interface.
- **Server (`openmanus_server/openmanus_server.py`)**: Server implementation for remote access.

## Key Features

1. **CodeAct Approach**: Uses executable Python code as the action mechanism.
2. **Iterative Agent Loop**: Analyze → Plan → Execute → Observe.
3. **Tool Integration**: Rich set of tools for environment interaction.
4. **Multiple Agent Types**: Different agent implementations for different use cases.
5. **Web and CLI Interfaces**: Multiple ways to interact with the system.

## Development Workflow

1. The agent receives a user prompt through either the CLI or web interface.
2. The agent analyzes the prompt and plans a solution.
3. The agent executes the plan using available tools.
4. The agent observes the results and iterates if necessary.
5. The agent returns the final results to the user.

## Configuration

Configuration is handled through files in the `config/` directory, allowing customization of:

- LLM providers and models
- Tool availability and behavior
- Agent parameters (max steps, observation limits, etc.)
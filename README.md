<p align="center">
  <img src="assets/logo.jpg" width="200"/>
</p>

English | [中文](README_zh.md) | [한국어](README_ko.md) | [日本語](README_ja.md)

[![GitHub stars](https://img.shields.io/github/stars/mannaandpoem/OpenManus?style=social)](https://github.com/mannaandpoem/OpenManus/stargazers)
&ensp;
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) &ensp;
[![Discord Follow](https://dcbadge.vercel.app/api/server/DYn29wFk9z?style=flat)](https://discord.gg/DYn29wFk9z)

# 👋 OpenManus

OpenManus is an autonomous AI agent that can perform complex tasks by interacting with your computer. It uses large language models (LLMs) to understand your instructions and execute them using tools like web browsers, shell commands, and code editors.

## Quick Start

Want to see OpenManus in action? Here's a simple example that creates a text file:

1.  **Installation:**

    We provide two installation methods. Method 2 (using uv) is recommended for faster installation and better dependency management.

    ### Method 1: Using conda

    1.  Create a new conda environment:

        ```bash
        conda create -n open_manus python=3.12
        conda activate open_manus
        ```

    2.  Clone the repository:

        ```bash
        git clone https://github.com/mannaandpoem/OpenManus.git
        cd OpenManus
        ```

    3.  Install dependencies:

        ```bash
        pip install -r requirements.txt
        ```

    ### Method 2: Using uv (Recommended)

    1.  Install uv (A fast Python package installer and resolver):

        ```bash
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```

    2.  Clone the repository:

        ```bash
        git clone https://github.com/mannaandpoem/OpenManus.git
        cd OpenManus
        ```

    3.  Create a new virtual environment and activate it:

        ```bash
        uv venv
        source .venv/bin/activate  # On Unix/macOS
        # Or on Windows:
        # .venv\Scripts\activate
        ```

    4.  Install dependencies:

        ```bash
        uv pip install -r requirements.txt
        ```

2.  **Configuration:**

    *   Create a `config.toml` file in the `config` directory:

        ```bash
        cp config/config.example.toml config/config.toml
        ```

    *   Edit `config/config.toml` and add your OpenAI API key:

        ```toml
        [llm]
        model = "gpt-4o"
        base_url = "https://api.openai.com/v1"
        api_key = "sk-..."  # Replace with your actual API key
        max_tokens = 4096
        temperature = 0.0
        ```
3. **Run OpenManus:**
   ```bash
    python main.py
   ```
4. **Input the following instruction in the terminal:**
   ```
    Create a file named 'hello.txt' in the workspace directory and write 'Hello, OpenManus!' into it.
   ```

OpenManus will create the file and write the text into it. You can find the file in the `workspace` directory.

## Key Features

- **Versatile File Operations**: The enhanced CodeEditor tool handles all file operations:
  - Create, modify, or save any type of file (code, text, data, etc.)
  - Support for both write and append modes
  - Automatic directory creation

- **Advanced Code Editing**: OpenManus features powerful code editing capabilities with multiple formats:
  - **Diff Format**: Make targeted changes to specific parts of files using SEARCH/REPLACE blocks
  - **Whole Format**: Create new files or completely rewrite existing ones
  - **Unified Diff Format**: Apply complex changes across multiple parts of a file

- **Repository Mapping**: Generate comprehensive maps of code repositories to understand structure and relationships

- **Web Browsing**: Interact with websites for information gathering and testing

- **Web Search**: Perform web searches using multiple search engines (Google, Baidu, DuckDuckGo)

- **Python Execution**: Run Python code to process data and automate tasks

- **Planning System**: Create and manage structured plans with step tracking and progress monitoring

- **MCP Integration**: Connect to Model Context Protocol (MCP) servers to extend functionality:
  - Register custom tools from MCP servers
  - Execute tools as part of the agent's workflow
  - Access external APIs and services

- **OpenManus Server**: A dedicated MCP server that exposes OpenManus tools as standardized APIs:
  - Browser automation
  - Google search
  - Python code execution
  - File saving
  - Termination control

- **Multiple Agent Types**:
  - **Manus**: A versatile general-purpose agent with comprehensive tools
  - **PlanningAgent**: An agent focused on creating and managing plans
  - **SWEAgent**: An autonomous AI programmer for software engineering tasks

## Use Cases
- **Automate repetitive tasks:**  Automate file manipulations, data processing, and other tasks.
- **Rapid prototyping:** Quickly create and test code snippets or scripts.
- **Web scraping and data extraction:** Gather information from websites.
- **Code refactoring and improvement:**  Make targeted changes to existing code.
- **Learning and experimentation:** Explore new libraries and APIs.

It's a simple implementation, so we welcome any suggestions, contributions, and feedback!

Enjoy your own agent with OpenManus!

We're also excited to introduce [OpenManus-RL](https://github.com/OpenManus/OpenManus-RL), an open-source project dedicated to reinforcement learning (RL)- based (such as GRPO) tuning methods for LLM agents, developed collaboratively by researchers from UIUC and OpenManus.

## Project Demo

<video src="https://private-user-images.githubusercontent.com/61239030/420168772-6dcfd0d2-9142-45d9-b74e-d10aa75073c6.mp4?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDEzMTgwNTksIm5iZiI6MTc0MTMxNzc1OSwicGF0aCI6Ii82MTIzOTAzMC80MjAxNjg3NzItNmRjZmQwZDItOTE0Mi00NWQ5LWI3NGUtZDEwYWE3NTA3M2M2Lm1wND9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTAzMDclMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwMzA3VDAzMjIzOVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTdiZjFkNjlmYWNjMmEzOTliM2Y3M2VlYjgyNDRlZDJmOWE3NWZhZjE1MzhiZWY4YmQ3NjdkNTYwYTU5ZDA2MzYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.UuHQCgWYkh0OQq9qsUWqGsUbhG3i9jcZDAMeHjLt5T4" data-canonical-src="https://private-user-images.githubusercontent.com/61239030/420168772-6dcfd0d2-9142-45d9-b74e-d10aa75073c6.mp4?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDEzMTgwNTksIm5iZiI6MTc0MTMxNzc1OSwicGF0aCI6Ii82MTIzOTAzMC80MjAxNjg3NzItNmRjZmQwZDItOTE0Mi00NWQ5LWI3NGUtZDEwYWE3NTA3M2M2Lm1wND9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTAzMDclMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwMzA3VDAzMjIzOVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTdiZjFkNjlmYWNjMmEzOTliM2Y3M2VlYjgyNDRlZDJmOWE3NWZhZjE1MzhiZWY4YmQ3NjdkNTYwYTU5ZDA2MzYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.UuHQCgWYkh0OQq9qsUWqGsUbhG3i9jcZDAMeHjLt5T4" controls="controls" muted="muted" class="d-block rounded-bottom-2 border-top width-fit" style="max-height:640px; min-height: 200px"></video>

### Using OpenManus Server

To use the OpenManus server with Claude for Desktop:

1. Install MCP dependencies:

```bash
uv pip install -r openmanus_server/mcp_requirements.txt
```

2. Configure Claude for Desktop to use the OpenManus server:

```json
{
    "mcpServers": {
        "openmanus": {
            "command": "/path/to/uv",
            "args": [
                "--directory",
                "/path/to/OpenManus/openmanus_server",
                "run",
                "openmanus_server.py"
            ]
        }
    }
}
```

<<<<<<< HEAD
3. Restart Claude for Desktop and look for the hammer icon to access the OpenManus tools.
=======
3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Method 2: Using uv (Recommended)

1. Install uv (A fast Python package installer and resolver):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:

```bash
git clone https://github.com/mannaandpoem/OpenManus.git
cd OpenManus
```

3. Create a new virtual environment and activate it:

```bash
uv venv --python 3.12
source .venv/bin/activate  # On Unix/macOS
# Or on Windows:
# .venv\Scripts\activate
```

4. Install dependencies:

```bash
uv pip install -r requirements.txt
```

## Configuration

OpenManus requires configuration for the LLM APIs it uses. Follow these steps to set up your configuration:

1. Create a `config.toml` file in the `config` directory (you can copy from the example):

```bash
cp config/config.example.toml config/config.toml
```

2. Edit `config/config.toml` to add your API keys and customize settings:

```toml
# Global LLM configuration
[llm]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
api_key = "sk-..."  # Replace with your actual API key
max_tokens = 4096
temperature = 0.0

# Optional configuration for specific LLM models
[llm.vision]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
api_key = "sk-..."  # Replace with your actual API key
```

## Quick Start

One line for run OpenManus:

```bash
python main.py
```

Then input your idea via terminal!

For unstable version, you also can run:

```bash
python run_flow.py
```
>>>>>>> 24b3d2d62c40c15472c1105e4deab92b5629052c

## How to contribute

We welcome any friendly suggestions and helpful contributions! Just create issues or submit pull requests.

Or contact @mannaandpoem via 📧email: mannaandpoem@gmail.com

**Note**: Before submitting a pull request, please use the pre-commit tool to check your changes. Run `pre-commit run --all-files` to execute the checks.

## Community Group
Join our networking group on Feishu and share your experience with other developers!

<div align="center" style="display: flex; gap: 20px;">
    <img src="assets/community_group.jpg" alt="OpenManus 交流群" width="300" />
</div>

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=mannaandpoem/OpenManus&type=Date)](https://star-history.com/#mannaandpoem/OpenManus&Date)

## Acknowledgement

Thanks to [anthropic-computer-use](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo)
and [browser-use](https://github.com/browser-use/browser-use) for providing basic support for this project!

Additionally, we are grateful to [AAAJ](https://github.com/metauto-ai/agent-as-a-judge), [MetaGPT](https://github.com/geekan/MetaGPT), [OpenHands](https://github.com/All-Hands-AI/OpenHands) and [SWE-agent](https://github.com/SWE-agent/SWE-agent).

OpenManus is built by contributors from MetaGPT. Huge thanks to this agent community!

## Cite
```bibtex
@misc{openmanus2025,
  author = {Xinbin Liang and Jinyu Xiang and Zhaoyang Yu and Jiayi Zhang and Sirui Hong},
  title = {OpenManus: An open-source framework for building general AI agents},
  year = {2025},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/mannaandpoem/OpenManus}},
}

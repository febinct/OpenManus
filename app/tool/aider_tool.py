import os
import subprocess
import tempfile
from typing import Dict, List, Optional

from app.tool.base import BaseTool, ToolResult


class AiderTool(BaseTool):
    """Tool for using Aider to assist with code-related tasks"""
    
    name: str = "aider"
    description: str = """Use Aider to assist with code-related tasks.
Aider is an AI pair programming tool that can help with coding tasks, refactoring, bug fixing, and more.
It works best with Claude 3.7 Sonnet, DeepSeek R1 & Chat V3, OpenAI o1, o3-mini & GPT-4o.
"""
    
    parameters: Dict = {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "The instruction or request to send to Aider. Can include file paths to analyze."
            },
            "model": {
                "type": "string",
                "description": "The model to use with Aider (e.g., 'claude-3-7-sonnet-latest', 'gpt-4o')",
                "default": "claude-3-7-sonnet-latest"
            }
        },
        "required": ["prompt"]
    }
    
    async def execute(
        self, 
        prompt: str, 
        model: str = "claude-3-7-sonnet-latest"
    ) -> ToolResult:
        """Execute Aider with the given parameters"""
        try:
            # Prepare command arguments
            cmd = [
                "aider",
                "--no-git",
                "--no-check-update",  # Suppress update check prompt
                "--no-show-release-notes",  # Suppress release notes
                "--yes-always",  # Automatically say yes to confirmations
                "--no-fancy-input",  # Disable fancy input (better for non-interactive use)
                "--model", model,
                "--message", prompt
            ]
            
            # Set up environment
            env = os.environ.copy()
            env["ANTHROPIC_BASE_URL"] = os.environ.get("ANTHROPIC_BASE_URL", "")
            env["ANTHROPIC_API_KEY"] = os.environ.get("ANTHROPIC_API_KEY", "anthropic")
            
            # Run Aider as a subprocess
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                env=env
            )
            
            # Extract Aider's response
            output = result.stdout
            
            # Find the AI's response in the output
            ai_response = output.split("AI: ")[-1] if "AI: " in output else output
            
            if result.returncode != 0:
                return ToolResult(
                    error=f"Aider exited with code {result.returncode}: {result.stderr}",
                    output=ai_response.strip()
                )
            
            return ToolResult(
                output=ai_response.strip()
            )
            
        except Exception as e:
            return ToolResult(
                error=f"Error running Aider: {str(e)}"
            )

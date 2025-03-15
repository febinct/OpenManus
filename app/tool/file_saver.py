import os
from pathlib import Path

import aiofiles

from app.config import OUTPUT_ROOT
from app.tool.base import BaseTool


class FileSaver(BaseTool):
    name: str = "file_saver"
    description: str = """Save content to a local file at a specified path.
Use this tool when you need to save text, code, or generated content to a file on the local filesystem.
By default, files are saved to the configured output directory (set in config.toml).
You can specify a relative path within the output directory, or set use_output_dir=False to save to an absolute path.
"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "(required) The content to save to the file."
            },
            "file_path": {
                "type": "string",
                "description": "(required) The path where the file should be saved including filename and extension."
            },
            "mode": {
                "type": "string",
                "description": "(optional) The file opening mode. Default is 'w' for write. Use 'a' for append.",
                "enum": ["w", "a"],
                "default": "w"
            },
            "use_output_dir": {
                "type": "boolean",
                "description": "(optional) Whether to save the file in the configured output directory. Default is True.",
                "default": True
            }
        },
        "required": ["content", "file_path"]
    }

    async def execute(self, content: str, file_path: str, mode: str = "w", use_output_dir: bool = True) -> str:
        """
        Save content to a file at the specified path.

        Args:
            content (str): The content to save to the file.
            file_path (str): The path where the file should be saved.
            mode (str, optional): The file opening mode. Default is 'w' for write. Use 'a' for append.
            use_output_dir (bool, optional): Whether to save the file in the configured output directory.
                                            Default is True. If False, the file will be saved at the exact path specified.

        Returns:
            str: A message indicating the result of the operation.
        """
        try:
            # Determine the full file path
            if use_output_dir:
                # Use the configured output directory
                full_path = OUTPUT_ROOT / file_path
            else:
                # Use the exact path specified
                full_path = Path(file_path)
            
            # Ensure the directory exists
            directory = os.path.dirname(str(full_path))
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            # Write directly to the file
            async with aiofiles.open(full_path, mode, encoding="utf-8") as file:
                await file.write(content)

            return f"Content successfully saved to {full_path}"
        except Exception as e:
            return f"Error saving file: {str(e)}"

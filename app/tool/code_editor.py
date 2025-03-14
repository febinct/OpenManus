import difflib
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import aiofiles
from pydantic import BaseModel, Field

from app.tool.base import BaseTool


class EditResult(BaseModel):
    """Result of a file edit operation"""
    success: bool
    message: str
    edited_files: List[str] = Field(default_factory=list)


class FileEditor(BaseTool):
    """Advanced file editing and creation tool with multiple formats for any file type"""
    
    name: str = "file_editor"
    description: str = """Edit or create any type of file using specialized formats for precise modifications.
Supports multiple edit formats for different types of changes:

1. DIFF MODE (format="diff"): For targeted edits to specific parts of files
   ```
   filename.py
   ```python
   <<<<<<< SEARCH
   def old_function():
       # old code
   =======
   def new_function():
       # new code
   >>>>>>> REPLACE
   ```
   Rules: SEARCH section must EXACTLY match existing code, including whitespace.
   For new files, use an empty SEARCH section.

2. WHOLE FILE MODE (format="whole"): For creating new files or complete rewrites
   ```
   filename.py
   ```python
   # Complete file content goes here
   # Never use ellipses (...) or omit any content
   ```
   Rules: Include the ENTIRE file content, never skip or abbreviate.

3. UNIFIED DIFF MODE (format="udiff"): For complex changes across multiple parts
   ```diff
   --- filename.py
   +++ filename.py
   @@ ... @@
   -def old_function():
   -    # old code
   +def new_function():
   +    # new code
   ```
   Rules: Include file paths, mark removed lines with - and added with +.

Also supports direct file saving by providing content and file_path parameters.
Can handle any type of file - code, configuration, data, text, etc."""
    
    parameters: Dict = {
        "type": "object",
        "properties": {
            "format": {
                "type": "string",
                "enum": ["whole", "diff", "udiff"],
                "description": "The edit format to use (whole file, search/replace blocks, or unified diff)"
            },
            "edits": {
                "type": "string",
                "description": "The edits to apply in the specified format"
            },
            "content": {
                "type": "string",
                "description": "Content to save to a file (direct file saving mode)"
            },
            "file_path": {
                "type": "string",
                "description": "Path where the content should be saved"
            },
            "mode": {
                "type": "string",
                "enum": ["w", "a"],
                "description": "File opening mode: 'w' for write (default), 'a' for append",
                "default": "w"
            }
        },
        "required": []
    }
    
    async def execute(self, format: str = "diff", edits: str = "", 
                     content: Optional[str] = None, 
                     file_path: Optional[str] = None,
                     mode: str = "w") -> str:
        """Execute file edits or creation using the specified format or direct content"""
        try:
            # Direct content mode (file saving)
            if content is not None and file_path is not None:
                try:
                    # Create directory if needed
                    directory = os.path.dirname(os.path.abspath(file_path))
                    if directory:
                        os.makedirs(directory, exist_ok=True)
                    
                    # Write the file using aiofiles for async I/O
                    async with aiofiles.open(file_path, mode, encoding="utf-8") as f:
                        await f.write(content)
                    
                    return f"Content successfully saved to {file_path}"
                except Exception as e:
                    return f"Error saving file: {str(e)}"
            
            # Standard FileEditor functionality
            if format == "whole":
                result = await self._apply_whole_file_edits(edits)
            elif format == "udiff":
                result = await self._apply_udiff_edits(edits)
            else:  # default to diff (search/replace blocks)
                result = await self._apply_diff_edits(edits)
                
            if result.success:
                return f"Successfully edited files: {', '.join(result.edited_files)}\n{result.message}"
            else:
                return f"Error applying edits: {result.message}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _apply_whole_file_edits(self, edits: str) -> EditResult:
        """Apply whole file edits"""
        edited_files = []
        errors = []
        
        # Extract file blocks using regex
        file_blocks = re.findall(r'([^\n]+)\n```(?:\w+)?\n(.*?)```', edits, re.DOTALL)
        
        if not file_blocks:
            return EditResult(
                success=False,
                message="No valid file blocks found. Format should be: filename.ext followed by ``` code ```"
            )
        
        for filename, content in file_blocks:
            filename = filename.strip()
            try:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
                
                # Write the file
                with open(filename, 'w') as f:
                    f.write(content)
                
                edited_files.append(filename)
            except Exception as e:
                errors.append(f"Error writing {filename}: {str(e)}")
        
        if errors:
            return EditResult(
                success=len(edited_files) > 0,
                message="\n".join(errors),
                edited_files=edited_files
            )
        
        return EditResult(
            success=True,
            message=f"Successfully edited {len(edited_files)} files",
            edited_files=edited_files
        )
    
    async def _apply_diff_edits(self, edits: str) -> EditResult:
        """Apply search/replace block edits"""
        edited_files = []
        errors = []
        
        # Extract search/replace blocks
        blocks = self._extract_search_replace_blocks(edits)
        
        if not blocks:
            return EditResult(
                success=False,
                message="No valid search/replace blocks found"
            )
        
        for filename, search_text, replace_text in blocks:
            try:
                # Check if file exists
                if not os.path.exists(filename) and not search_text.strip():
                    # Creating a new file
                    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
                    with open(filename, 'w') as f:
                        f.write(replace_text)
                    edited_files.append(filename)
                    continue
                
                # Read existing file
                with open(filename, 'r') as f:
                    content = f.read()
                
                # Apply the edit
                new_content = self._replace_text(content, search_text, replace_text)
                
                if new_content == content:
                    errors.append(f"No changes made to {filename} - search text not found")
                    continue
                
                # Write the updated content
                with open(filename, 'w') as f:
                    f.write(new_content)
                
                edited_files.append(filename)
            except Exception as e:
                errors.append(f"Error editing {filename}: {str(e)}")
        
        if errors:
            return EditResult(
                success=len(edited_files) > 0,
                message="\n".join(errors),
                edited_files=edited_files
            )
        
        return EditResult(
            success=True,
            message=f"Successfully edited {len(edited_files)} files",
            edited_files=edited_files
        )
    
    async def _apply_udiff_edits(self, edits: str) -> EditResult:
        """Apply unified diff edits"""
        edited_files = []
        errors = []
        
        # Extract diff blocks
        diff_blocks = re.findall(r'```diff\n(.*?)```', edits, re.DOTALL)
        
        if not diff_blocks:
            return EditResult(
                success=False,
                message="No valid diff blocks found"
            )
        
        for diff_block in diff_blocks:
            try:
                # Parse the diff to get filename and changes
                filename, changes = self._parse_diff(diff_block)
                
                if not filename:
                    errors.append("Could not determine filename from diff")
                    continue
                
                # Check if file exists
                if not os.path.exists(filename) and filename != '/dev/null':
                    # Creating a new file
                    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
                    with open(filename, 'w') as f:
                        f.write('\n'.join(line[1:] for line in changes if line.startswith('+')))
                    edited_files.append(filename)
                    continue
                
                # Read existing file
                with open(filename, 'r') as f:
                    content = f.read().splitlines()
                
                # Apply the diff
                new_content = self._apply_diff_changes(content, changes)
                
                # Write the updated content
                with open(filename, 'w') as f:
                    f.write('\n'.join(new_content))
                
                edited_files.append(filename)
            except Exception as e:
                errors.append(f"Error applying diff: {str(e)}")
        
        if errors:
            return EditResult(
                success=len(edited_files) > 0,
                message="\n".join(errors),
                edited_files=edited_files
            )
        
        return EditResult(
            success=True,
            message=f"Successfully edited {len(edited_files)} files",
            edited_files=edited_files
        )
    
    def _extract_search_replace_blocks(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract search/replace blocks from text"""
        blocks = []
        
        # Find all search/replace blocks
        pattern = r'([^\n]+)\n```(?:\w+)?\n<<<<<<< SEARCH\n(.*?)=======\n(.*?)>>>>>>> REPLACE\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for filename, search, replace in matches:
            blocks.append((filename.strip(), search, replace))
        
        return blocks
    
    def _replace_text(self, content: str, search: str, replace: str) -> str:
        """Replace search text with replace text in content"""
        # Try exact replacement first
        if search in content:
            return content.replace(search, replace, 1)
        
        # Try flexible matching if exact match fails
        search_lines = search.splitlines()
        content_lines = content.splitlines()
        
        for i in range(len(content_lines) - len(search_lines) + 1):
            # Check if this section matches
            match = True
            for j in range(len(search_lines)):
                if content_lines[i+j].rstrip() != search_lines[j].rstrip():
                    match = False
                    break
            
            if match:
                # Replace the matching section
                new_content = content_lines[:i] + replace.splitlines() + content_lines[i+len(search_lines):]
                return '\n'.join(new_content)
        
        # No match found
        return content
    
    def _parse_diff(self, diff: str) -> Tuple[str, List[str]]:
        """Parse a unified diff to extract filename and changes"""
        lines = diff.splitlines()
        filename = None
        changes = []
        
        # Extract filename from the diff header
        for i, line in enumerate(lines):
            if line.startswith('--- '):
                old_file = line[4:].strip()
                if i+1 < len(lines) and lines[i+1].startswith('+++ '):
                    new_file = lines[i+1][4:].strip()
                    filename = new_file if new_file != '/dev/null' else old_file
                    break
        
        # Extract changes
        in_hunk = False
        for line in lines:
            if line.startswith('@@ '):
                in_hunk = True
                continue
            
            if in_hunk and (line.startswith('+') or line.startswith('-') or line.startswith(' ')):
                changes.append(line)
        
        return filename, changes
    
    def _apply_diff_changes(self, content: List[str], changes: List[str]) -> List[str]:
        """Apply diff changes to content"""
        result = content.copy()
        i = 0
        
        for change in changes:
            if change.startswith(' '):
                # Context line - should match
                if i < len(result) and result[i].rstrip() == change[1:].rstrip():
                    i += 1
                else:
                    # Find the context line
                    context_line = change[1:]
                    for j in range(i, len(result)):
                        if result[j].rstrip() == context_line.rstrip():
                            i = j + 1
                            break
            elif change.startswith('-'):
                # Remove line
                if i < len(result) and result[i].rstrip() == change[1:].rstrip():
                    result.pop(i)
                else:
                    # Find the line to remove
                    remove_line = change[1:]
                    for j in range(i, len(result)):
                        if result[j].rstrip() == remove_line.rstrip():
                            result.pop(j)
                            break
            elif change.startswith('+'):
                # Add line
                result.insert(i, change[1:])
                i += 1
        
        return result

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from pydantic import BaseModel, Field

from app.tool.base import BaseTool


class RepoMapTool(BaseTool):
    """Tool for generating and managing repository maps"""
    
    name: str = "repo_map"
    description: str = "Generate a map of the repository to understand code structure"
    
    parameters: Dict = {
        "type": "object",
        "properties": {
            "root_path": {
                "type": "string",
                "description": "Root path of the repository"
            },
            "max_files": {
                "type": "integer",
                "description": "Maximum number of files to include in the map"
            },
            "include_patterns": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Patterns of files to include (e.g., '*.py', 'src/*')"
            },
            "exclude_patterns": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Patterns of files to exclude (e.g., '*.pyc', 'node_modules/*')"
            },
            "force_refresh": {
                "type": "boolean",
                "description": "Force refresh the repository map"
            }
        },
        "required": ["root_path"]
    }
    
    # Cache for repository maps
    _repo_maps: Dict[str, Dict] = {}
    
    async def execute(
        self, 
        root_path: str, 
        max_files: int = 100,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        force_refresh: bool = False
    ) -> str:
        """Generate a repository map"""
        try:
            # Normalize path
            root_path = os.path.abspath(root_path)
            
            # Check if we have a cached map
            cache_key = f"{root_path}:{max_files}:{include_patterns}:{exclude_patterns}"
            if not force_refresh and cache_key in self._repo_maps:
                cached_map = self._repo_maps[cache_key]
                if (datetime.now() - cached_map["timestamp"]).total_seconds() < 300:  # 5 minutes
                    return cached_map["content"]
            
            # Generate the map
            repo_map = await self._generate_map(
                root_path, 
                max_files,
                include_patterns or ["*.py", "*.js", "*.ts", "*.html", "*.css", "*.md"],
                exclude_patterns or ["**/node_modules/**", "**/__pycache__/**", "**/.git/**"]
            )
            
            # Cache the map
            self._repo_maps[cache_key] = {
                "content": repo_map,
                "timestamp": datetime.now()
            }
            
            return repo_map
        except Exception as e:
            return f"Error generating repository map: {str(e)}"
    
    async def _generate_map(
        self, 
        root_path: str, 
        max_files: int,
        include_patterns: List[str],
        exclude_patterns: List[str]
    ) -> str:
        """Generate a map of the repository"""
        # Get all files matching the patterns
        all_files = self._get_matching_files(root_path, include_patterns, exclude_patterns)
        
        # Limit to max_files
        if len(all_files) > max_files:
            all_files = self._prioritize_files(all_files, max_files)
        
        # Generate the map
        repo_map = "# Repository Map\n\n"
        
        # Add directory structure
        repo_map += "## Directory Structure\n\n"
        repo_map += self._generate_directory_structure(root_path, all_files)
        
        # Add file summaries
        repo_map += "\n## File Summaries\n\n"
        for file_path in all_files:
            rel_path = os.path.relpath(file_path, root_path)
            summary = self._generate_file_summary(file_path)
            repo_map += f"### {rel_path}\n\n{summary}\n\n"
        
        return repo_map
    
    def _get_matching_files(
        self, 
        root_path: str, 
        include_patterns: List[str],
        exclude_patterns: List[str]
    ) -> List[str]:
        """Get all files matching the patterns"""
        import fnmatch
        
        matching_files = []
        
        for root, _, files in os.walk(root_path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, root_path)
                
                # Check if file matches include patterns
                included = False
                for pattern in include_patterns:
                    if fnmatch.fnmatch(rel_path, pattern):
                        included = True
                        break
                
                if not included:
                    continue
                
                # Check if file matches exclude patterns
                excluded = False
                for pattern in exclude_patterns:
                    if fnmatch.fnmatch(rel_path, pattern):
                        excluded = True
                        break
                
                if excluded:
                    continue
                
                matching_files.append(file_path)
        
        return matching_files
    
    def _prioritize_files(self, files: List[str], max_files: int) -> List[str]:
        """Prioritize files to include in the map"""
        # Sort files by importance (e.g., README, main files, etc.)
        def file_priority(file_path: str) -> int:
            filename = os.path.basename(file_path).lower()
            if filename == "readme.md":
                return 0
            if filename in ["main.py", "app.py", "index.js", "package.json"]:
                return 1
            if "test" in filename:
                return 10
            return 5
        
        sorted_files = sorted(files, key=file_priority)
        return sorted_files[:max_files]
    
    def _generate_directory_structure(self, root_path: str, files: List[str]) -> str:
        """Generate a directory structure representation"""
        structure = "```\n"
        
        # Create a tree structure
        tree = {}
        for file_path in files:
            rel_path = os.path.relpath(file_path, root_path)
            parts = rel_path.split(os.sep)
            
            current = tree
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[parts[-1]] = None
        
        # Convert tree to string
        def print_tree(node, prefix="", is_last=True):
            result = ""
            if prefix:
                result += prefix + ("└── " if is_last else "├── ") + os.path.basename(node) + "\n"
            else:
                result += node + "\n"
            
            if isinstance(node, dict):
                items = list(node.items())
                for i, (key, value) in enumerate(items):
                    is_last_item = i == len(items) - 1
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    if value is None:
                        result += new_prefix + ("└── " if is_last_item else "├── ") + key + "\n"
                    else:
                        result += print_tree(value, new_prefix, is_last_item)
            
            return result
        
        structure += print_tree(os.path.basename(root_path))
        structure += "```\n"
        
        return structure
    
    def _generate_file_summary(self, file_path: str) -> str:
        """Generate a summary of a file"""
        try:
            # Get file extension
            ext = os.path.splitext(file_path)[1].lower()
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Generate summary based on file type
            if ext in ['.py', '.js', '.ts']:
                return self._summarize_code_file(content, ext)
            elif ext in ['.md', '.txt']:
                return self._summarize_text_file(content)
            elif ext in ['.json', '.toml', '.yaml', '.yml']:
                return self._summarize_config_file(content, ext)
            else:
                return f"File type: {ext}\nSize: {len(content)} bytes"
        except Exception as e:
            return f"Error summarizing file: {str(e)}"
    
    def _summarize_code_file(self, content: str, ext: str) -> str:
        """Summarize a code file"""
        lines = content.splitlines()
        
        # Extract imports
        imports = []
        if ext == '.py':
            import_lines = [line for line in lines if line.strip().startswith(('import ', 'from '))]
            imports = import_lines[:5]  # Limit to 5 imports
        elif ext in ['.js', '.ts']:
            import_lines = [line for line in lines if line.strip().startswith(('import ', 'require('))]
            imports = import_lines[:5]  # Limit to 5 imports
        
        # Extract classes and functions
        classes = []
        functions = []
        
        if ext == '.py':
            for line in lines:
                if line.strip().startswith('class '):
                    classes.append(line.strip())
                elif line.strip().startswith('def '):
                    functions.append(line.strip())
        elif ext in ['.js', '.ts']:
            for line in lines:
                if 'class ' in line:
                    classes.append(line.strip())
                elif 'function ' in line or '=>' in line:
                    functions.append(line.strip())
        
        # Limit to 5 classes and 10 functions
        classes = classes[:5]
        functions = functions[:10]
        
        # Generate summary
        summary = f"File type: {ext}\n"
        summary += f"Lines: {len(lines)}\n\n"
        
        if imports:
            summary += "**Imports:**\n```\n" + "\n".join(imports) + "\n```\n\n"
        
        if classes:
            summary += "**Classes:**\n```\n" + "\n".join(classes) + "\n```\n\n"
        
        if functions:
            summary += "**Functions:**\n```\n" + "\n".join(functions) + "\n```\n\n"
        
        return summary
    
    def _summarize_text_file(self, content: str) -> str:
        """Summarize a text file"""
        lines = content.splitlines()
        
        # Extract headings from markdown
        headings = []
        for line in lines:
            if line.strip().startswith('#'):
                headings.append(line.strip())
        
        # Limit to 10 headings
        headings = headings[:10]
        
        # Generate summary
        summary = f"File type: Text/Markdown\n"
        summary += f"Lines: {len(lines)}\n\n"
        
        if headings:
            summary += "**Headings:**\n" + "\n".join(headings) + "\n\n"
        
        # Include first few lines
        if lines:
            preview_lines = lines[:5]
            summary += "**Preview:**\n```\n" + "\n".join(preview_lines) + "\n```\n\n"
        
        return summary
    
    def _summarize_config_file(self, content: str, ext: str) -> str:
        """Summarize a configuration file"""
        lines = content.splitlines()
        
        # Generate summary
        summary = f"File type: Configuration ({ext})\n"
        summary += f"Lines: {len(lines)}\n\n"
        
        # Include first few lines
        if lines:
            preview_lines = lines[:10]
            summary += "**Preview:**\n```\n" + "\n".join(preview_lines) + "\n```\n\n"
        
        return summary

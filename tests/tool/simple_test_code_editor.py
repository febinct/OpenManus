import asyncio
import os
from app.tool.code_editor import CodeEditor

# Get the current directory (tests/tool)
TEST_DIR = os.path.dirname(os.path.abspath(__file__))

async def test_diff_format():
    """Test the diff format functionality of CodeEditor"""
    print("\n=== Testing CodeEditor Diff Format ===")
    
    # Test diff format
    test_diff_path = os.path.join(TEST_DIR, 'test_diff.py')
    
    # First, ensure the file exists with the content we expect
    with open(test_diff_path, 'w') as f:
        f.write("# Original content\n\ndef hello():\n    print('Hello, World!')\n")
    
    result = await CodeEditor().execute(
        format='diff',
        edits=f"""{test_diff_path}
```python
<<<<<<< SEARCH
def hello():
    print('Hello, World!')
=======
def hello():
    print('Hello, World! This is a modified version.')
>>>>>>> REPLACE
```"""
    )
    print(result)
    
    # Read the file to verify
    with open(test_diff_path, "r") as f:
        content = f.read()
    print(f"File content after edit: {content}")

if __name__ == "__main__":
    asyncio.run(test_diff_format())

import asyncio
import os
from app.tool.code_editor import CodeEditor
from app.agent.manus import Manus

# Get the current directory (tests/tool)
TEST_DIR = os.path.dirname(os.path.abspath(__file__))

async def test_code_editor_directly():
    """Test the CodeEditor tool directly"""
    print("\n=== Testing CodeEditor Tool Directly ===")
    
    # Test direct content saving in append mode
    test_file_path = os.path.join(TEST_DIR, 'test_file.txt')
    result = await CodeEditor().execute(
        direct_content='Appended content',
        file_path=test_file_path,
        mode='a'
    )
    print(result)
    
    # Test whole file format
    test_whole_path = os.path.join(TEST_DIR, 'test_whole.py')
    result = await CodeEditor().execute(
        format='whole',
        edits=f"""{test_whole_path}
```python
print("This is a test file created with whole format")
```"""
    )
    print(result)
    
    # Test diff format
    test_diff_path = os.path.join(TEST_DIR, 'test_diff.py')
    with open(test_diff_path, 'w') as f:
        f.write("# Original content\n\ndef hello():\n    print('Hello')\n")
    
    result = await CodeEditor().execute(
        format='diff',
        edits=f"""{test_diff_path}
```python
<<<<<<< SEARCH
def hello():
    print('Hello')
=======
def hello():
    print('Hello, World!')
>>>>>>> REPLACE
```"""
    )
    print(result)

async def test_manus_agent():
    """Test the Manus agent with CodeEditor replacing FileSaver"""
    print("\n=== Testing Manus Agent with CodeEditor ===")
    
    # Create a Manus agent
    agent = await Manus.create()
    
    # Test direct content saving with CodeEditor through Manus agent
    test_manus_path = os.path.join(TEST_DIR, 'test_manus_direct.txt')
    result = await agent.available_tools.execute(
        name="code_editor",
        tool_input={
            "direct_content": "This is a test file created with Manus agent using CodeEditor in direct content mode",
            "file_path": test_manus_path
        }
    )
    print(f"Direct content saving result: {result}")
    
    # Test appending with CodeEditor through Manus agent
    result = await agent.available_tools.execute(
        name="code_editor",
        tool_input={
            "direct_content": "\nThis line was appended",
            "file_path": test_manus_path,
            "mode": "a"
        }
    )
    print(f"Append result: {result}")
    
    # Read the file to verify
    with open(test_manus_path, "r") as f:
        content = f.read()
    print(f"File content: {content}")
    
    # Verify FileSaver is not available
    try:
        test_file_saver_path = os.path.join(TEST_DIR, 'test_file_saver.txt')
        result = await agent.available_tools.execute(
            name="file_saver",
            tool_input={
                "content": "This should fail",
                "file_path": test_file_saver_path
            }
        )
        print(f"FileSaver result (should not happen): {result}")
    except Exception as e:
        print(f"FileSaver test correctly failed with: {str(e)}")

if __name__ == "__main__":
    # Run both tests
    asyncio.run(test_code_editor_directly())
    asyncio.run(test_manus_agent())

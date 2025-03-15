import asyncio
import sys
from app.tool import AiderTool
from app.logger import logger

async def test_aider_tool():
    """Test the Aider tool with a simple prompt."""
    try:
        # Create an instance of the AiderTool
        aider_tool = AiderTool()
        
        # Define a simple prompt
        prompt = "Write a simple Python function to calculate the factorial of a number"
        
        # Execute the tool
        logger.info(f"Testing Aider tool with prompt: {prompt}")
        result = await aider_tool.execute(prompt=prompt)
        
        # Print the result
        print("\n--- Aider Tool Result ---")
        if result.error:
            print(f"Error: {result.error}")
        print(result.output)
        print("------------------------\n")
        
        return True
    except Exception as e:
        print(f"Error testing Aider tool: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_aider_tool())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Unhandled exception: {e}")
        sys.exit(1)

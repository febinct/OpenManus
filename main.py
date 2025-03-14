import asyncio

from app.agent.manus import Manus
from app.logger import logger


async def main():
    """Main entry point for the OpenManus CLI."""
    # Create the agent
    agent = await Manus.create()
    
    try:
        # Get user input
        prompt = input("Enter your prompt: ")
        if not prompt.strip():
            logger.warning("Empty prompt provided.")
            return

        # Process the request
        logger.warning("Processing your request...")
        await agent.run(prompt)
        logger.info("Request processing completed.")
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    except Exception as e:
        logger.error(f"Error: {str(e)}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        # Ignore known MCP SDK errors during shutdown
        if any(err_text in str(e) for err_text in [
            "Attempted to exit cancel scope in a different task",
            "Event loop is closed"
        ]):
            pass  # Silently ignore these errors
        else:
            logger.error(f"Runtime error: {e}")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")

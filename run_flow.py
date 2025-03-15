import asyncio
import argparse
import time

from app.agent.manus import Manus
from app.agent.swe import SWEAgent
from app.flow.base import FlowType
from app.flow.flow_factory import FlowFactory
from app.logger import logger



async def run_flow():
    
    # Create and initialize all available agents
    manus_agent = await Manus.create()
    swe_agent = await SWEAgent().create()
    
    # Create a dictionary of all agents
    all_agents = {
        "manus": manus_agent,
        "swe": swe_agent,
    }
    

    
    # Use the selected agent for the flow
    agents = all_agents

    try:
        prompt = input("Enter your prompt: ")

        if prompt.strip().isspace() or not prompt:
            logger.warning("Empty prompt provided.")
            return

        flow = FlowFactory.create_flow(
            flow_type=FlowType.PLANNING,
            agents=agents,
        )
        logger.warning("Processing your request...")

        try:
            start_time = time.time()
            result = await asyncio.wait_for(
                flow.execute(prompt),
                timeout=3600,  # 60 minute timeout for the entire execution
            )
            elapsed_time = time.time() - start_time
            logger.info(f"Request processed in {elapsed_time:.2f} seconds")
            logger.info(result)
        except asyncio.TimeoutError:
            logger.error("Request processing timed out after 1 hour")
            logger.info(
                "Operation terminated due to timeout. Please try a simpler request."
            )

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user.")
    except Exception as e:
        logger.error(f"Error: {str(e)}")


if __name__ == "__main__":
    try:
        asyncio.run(run_flow())
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

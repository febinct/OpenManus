#!/usr/bin/env python3
"""
Example MCP server for OpenManus.

This server provides a simple calculator tool that can perform basic arithmetic operations.
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Literal

from mcp.server.fastmcp import FastMCP, Context

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp-calculator")


# Define calculator context
@dataclass
class CalculatorContext:
    """Context for calculator operations."""
    operations_count: int = 0


@asynccontextmanager
async def calculator_lifespan(server: FastMCP) -> AsyncIterator[CalculatorContext]:
    """Manage calculator lifecycle with type-safe context."""
    try:
        # Initialize on startup
        logger.info("Initializing calculator server...")
        context = CalculatorContext()
        yield context
    finally:
        # Cleanup on shutdown
        logger.info(f"Shutting down calculator server. Total operations: {context.operations_count}")


# Create a named server with lifespan
calculator = FastMCP("calculator", lifespan=calculator_lifespan)



# Define calculator tool
@calculator.tool()
def calculate(ctx: Context, a: float, b: float, operation: Literal["add", "subtract", "multiply", "divide"]) -> str:
    """Perform a calculation on two numbers.

    Args:
        ctx: Tool context
        a: First number
        b: Second number
        operation: Operation to perform (add, subtract, multiply, divide)

    Returns:
        Result of the calculation
    """
    logger.info(f"Calculating {a} {operation} {b}")
    
    # Get lifespan context and increment operations count
    calc_context = ctx.request_context.lifespan_context
    calc_context.operations_count += 1

    result = None
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            return "Error: Cannot divide by zero"
        result = a / b

    return f"Result of {a} {operation} {b} = {result}"


# Define square root tool
@calculator.tool()
def sqrt(ctx: Context, number: float) -> str:
    """Calculate the square root of a number.

    Args:
        ctx: Tool context
        number: Number to calculate square root of

    Returns:
        Square root of the number
    """
    logger.info(f"Calculating square root of {number}")
    
    # Get lifespan context and increment operations count
    calc_context = ctx.request_context.lifespan_context
    calc_context.operations_count += 1

    if number < 0:
        return "Error: Cannot calculate square root of negative number"

    result = number ** 0.5
    return f"Square root of {number} = {result}"


if __name__ == "__main__":
    logger.info("Starting calculator MCP server")
    calculator.run(transport="stdio")

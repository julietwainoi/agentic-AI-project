import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP
from tools.calculator_tool import calculator

mcp = FastMCP("agentic-tools")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def greet(name: str) -> str:
    """Greet a user"""
    return f"Hello {name}"


@mcp.tool()
def calculator_tool(expression: str):
    """
    Evaluate a mathematical expression using the calculator tool
    """
    return calculator.execute({"expression": expression})


if __name__ == "__main__":
    mcp.run()
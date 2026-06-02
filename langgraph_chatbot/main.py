from __future__ import annotations
from fastmcp import FastMCP

mcp = FastMCP("arith")

def _as_number(x):
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        return float(x.strip())
    raise TypeError("Expected a number (int/float or numeric string)")

@mcp.tool()
async def add(a: float, b: float) -> float:
    return _as_number(a) + _as_number(b)

@mcp.tool()
async def sub(a: float, b: float) -> float:
    return _as_number(a) - _as_number(b)

@mcp.tool()
async def mul(a: float, b: float) -> float:
    return _as_number(a) * _as_number(b)

@mcp.tool()
async def div(a: float, b: float) -> float:
    denominator = _as_number(b)
    if denominator == 0:
        raise ValueError("Division by zero is not allowed.")
    return _as_number(a) / denominator

if __name__ == "__main__":
    mcp.run()
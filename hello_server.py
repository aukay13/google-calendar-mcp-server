from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hello-server")


@mcp.tool()
def say_hello(name: str) -> str:
    """Greet a person by name.

    Args:
        name: The name of the person to greet.

    Returns:
        A friendly greeting string addressed to the given name.
    """
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run(transport="stdio")

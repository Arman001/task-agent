from langchain.tools import tool


@tool
def calculator(expression: str) -> str:
    """Perform math calculations."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {e}"


@tool
def text_analyzer(text: str) -> str:
    """Analyze text statistics."""
    words = len(text.split())
    chars = len(text)
    lines = len(text.splitlines())

    return (
        f"Words: {words}\n"
        f"Characters: {chars}\n"
        f"Lines: {lines}"
    )

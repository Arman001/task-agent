from langchain.tools import tool
import os


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


@tool
def file_reader(path: str) -> str:
    """Read file contents. Use simple filenames like 'test.txt' for current directory."""
    try:
        # Clean the path - remove any placeholder paths
        if path.startswith('/path/to/'):
            path = path.replace('/path/to/', '')
        # Use current directory for simple filenames
        if not os.path.dirname(path):
            path = os.path.join(os.getcwd(), path)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"File content:\n{content}"
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def file_writer(path: str, content: str) -> str:
    """Write content to file. Use simple filenames like 'test.txt' for current directory."""
    try:
        # Clean the path - remove any placeholder paths
        if path.startswith('/path/to/'):
            path = path.replace('/path/to/', '')
        # Use current directory for simple filenames
        if not os.path.dirname(path):
            path = os.path.join(os.getcwd(), path)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {os.path.basename(path)}"
    except Exception as e:
        return f"Error writing file: {e}"


@tool
def file_checker(path: str) -> str:
    """Check if file exists. Use simple filenames like 'test.txt' for current directory."""
    # Clean the path - remove any placeholder paths
    if path.startswith('/path/to/'):
        path = path.replace('/path/to/', '')
    # Use current directory for simple filenames
    if not os.path.dirname(path):
        path = os.path.join(os.getcwd(), path)
    exists = os.path.exists(path)
    return f"File {os.path.basename(path)} {'exists' if exists else 'does not exist'}"

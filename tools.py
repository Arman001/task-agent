from langchain.tools import tool


@tool
def calculator(expression: str) -> str:
    """
    Performs mathematical calculations.
    Use this when you need to calculate numbers, percentages, or solve math problems.
    
    Args:
        expression: A mathematical expression as a string (e.g., "15 * 200 / 100")
    
    Returns:
        The calculated result as a string
    """
    try:
        # Safe evaluation of mathematical expressions
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Calculation result: {result}"
    except Exception as e:
        return f"Error in calculation: {str(e)}"


@tool
def text_analyzer(text: str) -> str:
    """
    Analyzes and provides information about text.
    Use this for tasks like counting words, characters, or basic text analysis.
    
    Args:
        text: The text to analyze
    
    Returns:
        Analysis results including word count, character count, etc.
    """
    words = len(text.split())
    characters = len(text)
    lines = len(text.split('\n'))
    
    return f"""Text Analysis:
- Words: {words}
- Characters: {characters}
- Lines: {lines}
- Average word length: {characters / words if words > 0 else 0:.1f}"""


@tool
def answer_question(question: str) -> str:
    """
    Use this when you can answer a question directly using your knowledge.
    Good for factual questions, definitions, explanations, etc.
    
    Args:
        question: The question to answer
    
    Returns:
        A signal that the LLM should answer directly
    """
    return f"ANSWER_DIRECTLY: {question}"
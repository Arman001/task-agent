from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    The state that flows through our agent.
    Keep it simple for Phase 1.
    """
    # What the user wants done
    task: str
    
    # What action the agent decides to take
    action: str
    
    # The final result/output
    result: str
    
    # Messages for LangGraph (tracks conversation)
    messages: Annotated[list, add_messages]
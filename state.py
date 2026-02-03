from typing import List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated

class AgentState(TypedDict):
    task: str
    complexity: str  # SIMPLE or COMPLEX
    plan: List[str]  # List of planned steps
    current_step: int  # Current step index
    step_results: List[str]  # Results from each step
    result: str
    messages: Annotated[List[BaseMessage], add_messages]

from typing import List, Dict, Any
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
    
    # Phase 3: Error handling and retry
    errors: List[Dict[str, Any]]  # Track errors with context
    retry_count: int  # Number of retries for current step
    max_retries: int  # Maximum retries allowed
    tool_status: Dict[str, str]  # Track success/failure per tool
    fallback_triggered: bool  # Whether fallback path was used

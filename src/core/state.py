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
    
    # Phase 4: Memory fields
    session_id: str  # Current session UUID
    memory_context: Dict[str, Any]  # Retrieved memories
    should_save_memory: bool  # Flag to save this task
    
    # Phase 5: Feedback & Control fields
    pending_approval: Dict[str, Any]  # Optional action awaiting approval
    approval_granted: bool  # User decision (True/False)
    approval_history: List[Dict[str, Any]]  # Past approval decisions
    user_preferences: Dict[str, str]  # Approval rules per action type
    risk_level: str  # Current step risk: SAFE/MODERATE/CRITICAL
    skip_current_step: bool  # Flag to skip rejected steps
    
    # Phase 6: Code Execution fields
    code_executions: List[Dict[str, Any]]  # Stores multiple executions (complex path)
    code_to_execute: str  # Legacy
    execution_output: str  # Legacy 
    generated_files: List[str]  # Legacy

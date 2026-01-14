from typing import List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated

class AgentState(TypedDict):
    task: str
    result: str
    messages: Annotated[List[BaseMessage], add_messages]

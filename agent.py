from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
import os
from langchain_core.messages import SystemMessage, HumanMessage

from state import AgentState
from tools import calculator, text_analyzer

load_dotenv()


# -------------------------
# Helper: normalize Gemini output
# -------------------------
def extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict)
        )
    return str(content)


# -------------------------
# LLM
# -------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

tools = [calculator, text_analyzer]
llm_with_tools = llm.bind_tools(tools)


# -------------------------
# Agent node (LLM only)
# -------------------------
def agent_node(state: AgentState) -> AgentState:
    messages = state.get("messages", [])

    if not messages:
        system_prompt = SystemMessage(content=f"""
You are a task automation assistant.
You must use tools when appropriate.
Available tools:
- calculator(expression: str): Use for any math calculations.
- text_analyzer(text: str): Use to analyze or summarize text.

Rules:
1. Always call a tool if the user asks for math or text analysis.
2. Do NOT answer directly unless the task cannot use any tool.
3. Return your answer only after the tool is called.
4. Never just repeat the user input.

Current task: {state['task']}
""")
        user_msg = HumanMessage(content=state['task'])
        messages.extend([system_prompt, user_msg])

    response = llm_with_tools.invoke(messages)
    state["messages"].append(response)

    if not getattr(response, "tool_calls", None):
        state["result"] = extract_text(response.content)

    return state

# -------------------------
# Router
# -------------------------
def should_continue(state: AgentState) -> str:
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"
    return END


# -------------------------
# Build graph
# -------------------------
def create_agent():
    workflow = StateGraph(AgentState)

    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", END: END},
    )

    workflow.add_edge("tools", "agent")

    return workflow.compile()


agent = create_agent()

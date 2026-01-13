from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
import os
import time

from state import AgentState
from tools import calculator, text_analyzer, answer_question

# Load environment variables
load_dotenv()


# Initialize Gemini LLM with rate limiting
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",  # Use stable gemini-pro model
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    request_timeout=30,
    max_retries=2
)

# Bind tools to the LLM
tools = [calculator, text_analyzer, answer_question]
llm_with_tools = llm.bind_tools(tools)


# Define the agent's decision node
def agent_node(state: AgentState) -> AgentState:
    """
    The agent analyzes the task and decides what to do.
    """
    task = state["task"]
    
    # Add rate limiting delay
    time.sleep(2)
    
    # Create a message for the LLM
    messages = state.get("messages", [])
    
    # If this is the first call, add the task
    if len(messages) == 0:
        messages.append({
            "role": "user",
            "content": f"Please help with this task: {task}"
        })
    
    try:
        # Get LLM response with tool calling capability
        response = llm_with_tools.invoke(messages)
        
        # Update state with the response
        state["messages"].append(response)
        
        # Check if LLM wants to use a tool
        if response.tool_calls:
            tool_call = response.tool_calls[0]
            state["action"] = tool_call["name"]
        else:
            state["action"] = "answer_directly"
            state["result"] = response.content
            
    except Exception as e:
        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            print("⏳ Rate limit hit, waiting 15 seconds...")
            time.sleep(15)
            # Provide a fallback response based on task type
            if "summarize" in task.lower() or "summary" in task.lower():
                # Extract text between quotes for summarization
                import re
                quoted_text = re.findall(r'"([^"]+)"', task)
                if quoted_text:
                    text = quoted_text[0]
                    # Simple summarization fallback
                    sentences = text.split('. ')
                    summary = f"Summary: {sentences[0]}. This text discusses {len(sentences)} main points about the topic."
                    state["result"] = summary
                else:
                    state["result"] = "I can help summarize text, but I need the text to be provided clearly."
            elif any(op in task.lower() for op in ['+', '-', '*', '/', 'add', 'subtract', 'multiply', 'divide']):
                state["action"] = "calculator"
            else:
                state["result"] = f"Due to API limits, please try again in a few minutes or upgrade your API plan."
            state["action"] = "answer_directly"
        else:
            raise e
    
    return state


# Define the tool execution node
def tool_node(state: AgentState) -> AgentState:
    """
    Executes the tool the agent decided to use.
    """
    # ToolNode from LangGraph handles tool execution automatically
    return state


# Define the router - decides where to go next
def should_continue(state: AgentState) -> str:
    """
    Determines if we need to call a tool or if we're done.
    """
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None
    
    # If the last message has tool calls, route to tools
    if last_message and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    # Otherwise, we're done
    return "end"


# Build the graph
def create_agent():
    """
    Creates the LangGraph agent.
    """
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    
    # After tools, go back to agent to process results
    workflow.add_edge("tools", "agent")
    
    # Compile the graph
    return workflow.compile()


# Create the agent instance
agent = create_agent()
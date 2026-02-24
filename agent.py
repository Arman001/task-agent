from langchain_groq import ChatGroq
# from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
import os
import time
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage

from state import AgentState
from tools import calculator, text_analyzer, file_reader, file_writer, file_checker, web_search, http_request, url_fetch, api_weather
import config
from memory_nodes import memory_retrieval_node, memory_writer_node
import uuid

load_dotenv()


# -------------------------
# Helper: normalize output
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
# LLM - Groq (Fast & Free)
# -------------------------
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.0,
    groq_api_key=os.getenv("GROQ_API_KEY"),
)

tools = [calculator, text_analyzer, file_reader, file_writer, file_checker, web_search, http_request, url_fetch, api_weather]
llm_with_tools = llm.bind_tools(tools)


# -------------------------
# Task Complexity Analyzer
# -------------------------
def analyze_complexity(state: AgentState) -> AgentState:
    task = state['task']
    
    # Initialize Phase 3 fields if not present
    if 'errors' not in state:
        state['errors'] = []
    if 'retry_count' not in state:
        state['retry_count'] = 0
    if 'max_retries' not in state:
        state['max_retries'] = config.MAX_RETRIES
    if 'tool_status' not in state:
        state['tool_status'] = {}
    if 'fallback_triggered' not in state:
        state['fallback_triggered'] = False
    
    complexity_prompt = f"""
Analyze if this task requires multiple steps or can be done in one step.

Task: {task}

Respond with ONLY:
- "SIMPLE" if it's a single action (math, text analysis, direct question, single web search, weather check, news search)
- "COMPLEX" if it needs multiple coordinated steps (file operations + analysis, creating reports from files)

Examples:
- "Calculate 5+3" → SIMPLE
- "What is AI?" → SIMPLE  
- "What's the weather in Paris?" → SIMPLE
- "Search for AI agents" → SIMPLE
- "Search for latest news" → SIMPLE
- "Create a report from data.txt" → COMPLEX
- "Read file, analyze it, and create summary report" → COMPLEX
"""
    
    response = llm.invoke([HumanMessage(content=complexity_prompt)])
    complexity = extract_text(response.content).strip()
    
    state['complexity'] = complexity
    print(f"🔍 Task complexity: {complexity}")
    return state


# -------------------------
# Planner Node
# -------------------------
def planner_node(state: AgentState) -> AgentState:
    task = state['task']
    
    planning_prompt = f"""
Break down this complex task into clear, sequential steps.

Task: {task}

Available tools:
- file_checker, file_reader, file_writer, text_analyzer, calculator
- web_search: Search the internet (USE THIS for research, don't fetch URLs manually)
- http_request, url_fetch, api_weather

IMPORTANT RULES:
1. Keep plans SIMPLE: 2-5 steps MAXIMUM - NO EXCEPTIONS
2. For search/research tasks: Use web_search ONLY - don't fetch URLs manually
3. Don't create unnecessary file operations
4. Use simple filenames like 'test.txt', 'report.txt'
5. Each step should use ONE tool only. NEVER combine reading and analyzing in a single step.
6. If you need to analyze a file, you MUST explicitly include a step to read it first (e.g. Step 1: Write file, Step 2: Read file, Step 3: Analyze text from previous step).

BAD PLAN (DON'T DO THIS):
1. Search for sources
2. Check if sources.txt exists
3. Write sources to file
4. Fetch URLs from sources...
(This is 14 steps - TOO COMPLEX!)

GOOD PLAN:
1. Search for information
2. Summarize findings
(This is 2 steps - PERFECT!)

Return ONLY a numbered list of steps:
1. [First step]
2. [Second step]
"""
    
    response = llm.invoke([HumanMessage(content=planning_prompt)])
    plan_text = extract_text(response.content).strip()
    
    # Parse steps
    steps = []
    for line in plan_text.split('\n'):
        if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith('-')):
            # Remove numbering
            step = line.split('.', 1)[-1].strip() if '.' in line else line.strip()
            steps.append(step)
    
    state['plan'] = steps
    state['current_step'] = 0
    state['step_results'] = []
    
    print(f"📋 Created plan with {len(steps)} steps:")
    for i, step in enumerate(steps, 1):
        print(f"  {i}. {step}")
    print()
    
    return state


# -------------------------
# Executor Node (with retry logic)
# -------------------------
def executor_node(state: AgentState) -> AgentState:
    current_step = state['current_step']
    plan = state['plan']
    
    if current_step >= len(plan):
        return state
    
    step_task = plan[current_step]
    
    # Handle retry with exponential backoff
    if state['retry_count'] > 0:
        backoff_delay = config.BACKOFF_BASE ** state['retry_count']
        print(f"⏳ Retry {state['retry_count']}/{state['max_retries']} after {backoff_delay}s delay...")
        time.sleep(backoff_delay)
    
    print(f"⚡ Executing step {current_step + 1}: {step_task}")
    
    # Build context from previous results
    context = ""
    if state['step_results']:
        context = "\nPrevious step results:\n" + "\n".join(
            f"Step {i+1}: {result}" for i, result in enumerate(state['step_results'])
        )
    
    system_prompt = SystemMessage(content="You are a helpful assistant executing one step of a plan. Use the correct tool for the instructions.")
    
    user_msg = HumanMessage(content=f"Context: {context}\n\nCurrent step to execute: {step_task}")
    messages = [system_prompt, user_msg]
    
    try:
        response = llm_with_tools.invoke(messages)
        
        # Handle tool calls
        if getattr(response, "tool_calls", None):
            tool_node = ToolNode(tools)
            tool_result = tool_node.invoke({"messages": [response]})
            step_result = extract_text(tool_result['messages'][-1].content)
            
            # Check for errors in tool result
            if "error" in step_result.lower() or "failed" in step_result.lower():
                raise Exception(step_result)
                
            # Log specific tool name success for performance stats
            actual_tool_name = response.tool_calls[0].get("name", "unknown")
            state['tool_status'][actual_tool_name] = "success"
        else:
            step_result = extract_text(response.content)
        
        # Success - reset retry count
        state['step_results'].append(step_result)
        state['current_step'] += 1
        state['retry_count'] = 0
        state['tool_status'][f"step_{current_step}"] = "success"
        
        print(f"✅ Step {current_step + 1} result: {step_result}\n")
        
    except Exception as e:
        error_info = {
            "step": current_step,
            "task": step_task,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        state['errors'].append(error_info)
        state['tool_status'][f"step_{current_step}"] = "failed"
        print(f"❌ Step {current_step + 1} failed: {str(e)}")
    
    return state


# -------------------------
# Simple Agent Node (Phase 1 behavior)
# -------------------------
def simple_agent_node(state: AgentState) -> dict:
    messages = state.get("messages", [])
    new_messages = []

    if not messages:
        # Build memory context string
        memory_str = ""
        memory_context = state.get('memory_context', {})
        if memory_context.get('session_history'):
            memory_str = "\nRecent Session History:\n" + "\n".join(
                f"- User: {item['task']}\n  Result: {item['result'][:150]}..." 
                for item in memory_context['session_history']
            )

        system_prompt = SystemMessage(content="You are a helpful assistant. Use tools if necessary. If the answer is in the recent history, answer directly.")
        user_msg = HumanMessage(content=f"Recent History: {memory_str}\n\nTask: {state['task']}")
        current_messages = [system_prompt, user_msg]
        new_messages.extend([system_prompt, user_msg])
    else:
        current_messages = list(messages)

    response = llm_with_tools.invoke(current_messages)
    new_messages.append(response)
    
    updates = {"messages": new_messages}

    if getattr(response, "tool_calls", None):
        for tool_call in response.tool_calls:
            tool_name = tool_call.get("name", "unknown")
            print(f"🔧 Using tool: {tool_name}")
    else:
        # No tool calls, this is the final response
        result = extract_text(response.content)
        if result and result.strip():
            updates["result"] = result

    return updates


# -------------------------
# Phase 3: Error Handler Node
# -------------------------
def error_handler_node(state: AgentState) -> AgentState:
    """Analyze errors and decide on retry or fallback."""
    if not state['errors']:
        return state
    
    last_error = state['errors'][-1]
    print(f"⚠️  Error handler analyzing: {last_error['error'][:100]}")
    
    # Check if we should retry
    if state['retry_count'] < state['max_retries']:
        state['retry_count'] += 1
        print(f"🔄 Will retry (attempt {state['retry_count']}/{state['max_retries']})")
    else:
        # Max retries reached, trigger fallback
        print(f"⛔ Max retries reached, triggering fallback")
        state['fallback_triggered'] = True
        state['retry_count'] = 0
    
    return state


# -------------------------
# Phase 3: Fallback Planner Node
# -------------------------
def fallback_planner_node(state: AgentState) -> AgentState:
    """Create alternate plan when primary approach fails."""
    current_step = state['current_step']
    failed_step = state['plan'][current_step] if current_step < len(state['plan']) else "unknown"
    
    print(f"🔀 Creating fallback plan for failed step: {failed_step}")
    
    fallback_prompt = f"""
The following step failed after multiple retries:
{failed_step}

Error: {state['errors'][-1]['error'] if state['errors'] else 'Unknown error'}

Provide ONE simple alternative action:
- If it's a URL fetch that failed, respond: "SKIP"
- If it's a file operation, suggest checking the file first
- If it's an API call, suggest using web_search instead

Respond with ONLY:
- "SKIP" to skip this step, OR
- One short alternative step (max 10 words)

Examples:
- "SKIP"
- "Use web_search for the information"
- "Check if file exists first"
"""
    
    response = llm.invoke([HumanMessage(content=fallback_prompt)])
    fallback_step = extract_text(response.content).strip()
    
    if fallback_step.upper() == "SKIP" or "skip" in fallback_step.lower():
        print(f"⏭️  Skipping failed step")
        state['step_results'].append(f"[SKIPPED: {failed_step}]")
        state['current_step'] += 1
    else:
        print(f"🔄 Fallback approach: {fallback_step}")
        state['plan'][current_step] = fallback_step
    
    # Clear errors and reset for new attempt
    state['errors'] = []
    state['fallback_triggered'] = False
    
    return state


# -------------------------
# Coordinator Node
# -------------------------
def coordinator_node(state: AgentState) -> AgentState:
    plan = state['plan']
    step_results = state['step_results']
    
    # Compile final result
    result_summary = f"Completed {len(step_results)} steps:\n\n"
    for i, (step, result) in enumerate(zip(plan, step_results), 1):
        status = state['tool_status'].get(f"step_{i-1}", "unknown")
        icon = "✅" if status == "success" else "⚠️"
        result_summary += f"{icon} Step {i}: {step}\n→ {result}\n\n"
    
    # Add error summary if any failures occurred
    if state['errors']:
        result_summary += f"\n⚠️  Encountered {len(state['errors'])} error(s) during execution\n"
    
    if state.get('fallback_triggered') or any('SKIP' in r for r in step_results):
        result_summary += "\n🔀 Fallback strategies were used\n"
    
    state['result'] = result_summary.strip()
    return state


# -------------------------
# Routers
# -------------------------
def complexity_router(state: AgentState) -> str:
    complexity = state.get('complexity', 'SIMPLE')
    if complexity == 'COMPLEX':
        return "planner"
    return "simple_agent"


def simple_agent_router(state: AgentState) -> str:
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"
    return END


def execution_router(state: AgentState) -> str:
    """Route based on errors, retries, and step completion."""
    current_step = state['current_step']
    
    # Check if the step we are currently on has failed
    step_status = state['tool_status'].get(f"step_{current_step}")
    
    if step_status == "failed" and not state['fallback_triggered']:
        # Check if we should retry
        if state['retry_count'] < state['max_retries']:
            return "error_handler"
        else:
            # Max retries reached, go to fallback
            return "error_handler"
    
    # Check if fallback was triggered
    if state['fallback_triggered']:
        return "fallback_planner"
    
    # Check if more steps remain
    current_step = state['current_step']
    plan = state['plan']
    
    if current_step < len(plan):
        return "executor"
    return "coordinator"


# -------------------------
# Build Graph
# -------------------------
def create_agent():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("analyzer", analyze_complexity)
    workflow.add_node("planner", planner_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("simple_agent", simple_agent_node)
    workflow.add_node("tools", ToolNode(tools))
    
    # Phase 3: Error handling nodes
    workflow.add_node("error_handler", error_handler_node)
    workflow.add_node("fallback_planner", fallback_planner_node)

    # NEW Phase 4 nodes
    workflow.add_node("memory_retrieval", memory_retrieval_node)
    workflow.add_node("memory_writer", memory_writer_node)

    # NEW: Memory retrieval is now the entry point
    workflow.set_entry_point("memory_retrieval")

    # Add edges
    
    # Memory retrieval → Analyzer
    workflow.add_edge("memory_retrieval", "analyzer")

    workflow.add_conditional_edges(
        "analyzer",
        complexity_router,
        {"planner": "planner", "simple_agent": "simple_agent"}
    )
    
    workflow.add_edge("planner", "executor")
    
    workflow.add_conditional_edges(
        "executor",
        execution_router,
        {
            "executor": "executor",
            "coordinator": "coordinator",
            "error_handler": "error_handler",
            "fallback_planner": "fallback_planner"
        }
    )
    
    # Phase 3: Error handling edges
    workflow.add_edge("error_handler", "executor")  # Retry
    workflow.add_edge("fallback_planner", "executor")  # Try fallback
    
    # NEW: Coordinator → Memory Writer → END
    workflow.add_edge("coordinator", "memory_writer")
    workflow.add_edge("memory_writer", END)
    
    workflow.add_conditional_edges(
        "simple_agent",
        simple_agent_router,
        {"tools": "tools", END: "memory_writer"}
    )
    
    workflow.add_edge("tools", "simple_agent")

    return workflow.compile()


agent = create_agent()


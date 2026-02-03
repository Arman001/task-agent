from langchain_groq import ChatGroq
# from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
import os
from langchain_core.messages import SystemMessage, HumanMessage

from state import AgentState
from tools import calculator, text_analyzer, file_reader, file_writer, file_checker

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
    model="llama-3.1-8b-instant",
    temperature=0.7,
    groq_api_key=os.getenv("GROQ_API_KEY"),
)

tools = [calculator, text_analyzer, file_reader, file_writer, file_checker]
llm_with_tools = llm.bind_tools(tools)


# -------------------------
# Task Complexity Analyzer
# -------------------------
def analyze_complexity(state: AgentState) -> AgentState:
    task = state['task']
    
    complexity_prompt = f"""
Analyze if this task requires multiple steps or can be done in one step.

Task: {task}

Respond with ONLY:
- "SIMPLE" if it's a single action (math, text analysis, direct question)
- "COMPLEX" if it needs multiple coordinated steps (file operations + analysis, multi-step workflows)

Examples:
- "Calculate 5+3" → SIMPLE
- "What is AI?" → SIMPLE  
- "Create a report from data.txt" → COMPLEX
- "Read file.txt and count words" → COMPLEX
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
- file_checker: Check if file exists (use simple names like 'test.txt')
- file_reader: Read file contents (use simple names like 'test.txt')
- text_analyzer: Get text statistics
- calculator: Math operations
- file_writer: Write content to file (use simple names like 'test.txt')

IMPORTANT: Use simple filenames like 'test.txt', 'report.txt' - NOT full paths.

Return ONLY a numbered list of steps, one per line:
1. [First step]
2. [Second step]
3. [Third step]
...

Example for "Create summary of data.txt":
1. Check if data.txt exists
2. Read data.txt contents
3. Analyze text statistics
4. Write summary to report.txt
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
# Executor Node
# -------------------------
def executor_node(state: AgentState) -> AgentState:
    current_step = state['current_step']
    plan = state['plan']
    
    if current_step >= len(plan):
        return state
    
    step_task = plan[current_step]
    print(f"⚡ Executing step {current_step + 1}: {step_task}")
    
    # Build context from previous results
    context = ""
    if state['step_results']:
        context = "\nPrevious step results:\n" + "\n".join(
            f"Step {i+1}: {result}" for i, result in enumerate(state['step_results'])
        )
    
    system_prompt = SystemMessage(content=f"""
You are executing one step of a multi-step plan.
Current step: {step_task}
{context}

Available tools:
- calculator: Math operations
- text_analyzer: Text statistics  
- file_checker: Check file existence
- file_reader: Read file contents
- file_writer: Write content to file

Execute this step using the appropriate tool if needed, or provide a direct response.
""")
    
    user_msg = HumanMessage(content=step_task)
    messages = [system_prompt, user_msg]
    
    response = llm_with_tools.invoke(messages)
    
    # Handle tool calls
    if getattr(response, "tool_calls", None):
        # Execute tools
        tool_node = ToolNode(tools)
        tool_result = tool_node.invoke({"messages": [response]})
        step_result = extract_text(tool_result['messages'][-1].content)
    else:
        step_result = extract_text(response.content)
    
    state['step_results'].append(step_result)
    state['current_step'] += 1
    
    print(f"✅ Step {current_step + 1} result: {step_result}\n")
    
    return state


# -------------------------
# Simple Agent Node (Phase 1 behavior)
# -------------------------
def simple_agent_node(state: AgentState) -> AgentState:
    messages = state.get("messages", [])

    if not messages:
        system_prompt = SystemMessage(content=f"""
You are a task automation assistant.
Available tools:
- calculator: Math calculations
- text_analyzer: Text statistics
- file_checker: Check file existence
- file_reader: Read file contents
- file_writer: Write content to file

Current task: {state['task']}
""")
        user_msg = HumanMessage(content=state['task'])
        messages.extend([system_prompt, user_msg])

    response = llm_with_tools.invoke(messages)
    state["messages"].append(response)

    if getattr(response, "tool_calls", None):
        for tool_call in response.tool_calls:
            tool_name = tool_call.get("name", "unknown")
            print(f"🔧 Using tool: {tool_name}")
    else:
        state["result"] = extract_text(response.content)

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
        result_summary += f"Step {i}: {step}\n→ {result}\n\n"
    
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

    # Set entry point
    workflow.set_entry_point("analyzer")

    # Add edges
    workflow.add_conditional_edges(
        "analyzer",
        complexity_router,
        {"planner": "planner", "simple_agent": "simple_agent"}
    )
    
    workflow.add_edge("planner", "executor")
    
    workflow.add_conditional_edges(
        "executor",
        execution_router,
        {"executor": "executor", "coordinator": "coordinator"}
    )
    
    workflow.add_edge("coordinator", END)
    
    workflow.add_conditional_edges(
        "simple_agent",
        simple_agent_router,
        {"tools": "tools", END: END}
    )
    
    workflow.add_edge("tools", "simple_agent")

    return workflow.compile()


agent = create_agent()


from langchain_core.messages import ToolMessage
from datetime import datetime

from src.core.state import AgentState
from src.approval.classifier import classify_action
from src.approval.preferences import preference_manager
from src.approval.logger import approval_logger

from rich.panel import Panel
from rich.syntax import Syntax

from src.core.ui import console, agent_status

def _get_action_type_from_step(step_desc: str, tool_name: str) -> str:
    """Helper to map a tool or step description to preference action type."""
    tool_name = tool_name.replace("step_", "")
    if tool_name in ["file_reader", "file_checker"]:
        return "file_read"
    if tool_name == "file_writer":
        return "file_write"
    if tool_name == "calculator":
        return "calculation"
    if tool_name == "text_analyzer":
        return "text_analyze"
    if tool_name == "web_search":
        return "web_search"
    if tool_name == "http_request":
        if "post" in step_desc.lower():
            return "http_post"
        return "http_request"
    
    desc_lower = step_desc.lower()
    if "delete" in desc_lower or "remove" in desc_lower:
        return "file_delete"
    
    return tool_name

def risk_classifier_node(state: AgentState) -> AgentState:
    """Analyzes planned steps and assigns risk levels."""
    
    if state.get('complexity') == 'COMPLEX':
        current_step_idx = state.get('current_step', 0)
        plan = state.get('plan', [])
        if current_step_idx < len(plan):
            step_desc = plan[current_step_idx]
            # Try to guess tool name from text or just let classifier handle via desc keyword
            tool_guessed = next((t for t in ["python_executor", "file_writer", "file_reader", "web_search", "calculator", "http_request", "file_deleter", "file_checker", "url_fetch", "api_weather"] if t in step_desc), "")
            risk_level = classify_action(step_desc, tool_guessed)
        else:
            step_desc = "Unknown"
            tool_guessed = ""
            risk_level = "SAFE"
    else:
        # Simple path
        messages = state.get('messages', [])
        step_desc = state.get('task', "Unknown")
        tool_guessed = "unknown"
        if messages:
            last_msg = messages[-1]
            if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                tool_names = [tc.get("name", "") for tc in last_msg.tool_calls]
                tool_guessed = tool_names[0] if tool_names else "unknown"
                for t in tool_names:
                    if t in ["python_executor", "file_writer", "http_request", "url_fetch", "file_deleter"]:
                        tool_guessed = t
                        break
                
                args_str = " | ".join([str(tc.get('args', {})) for tc in last_msg.tool_calls])
                step_desc = f"Task: {state.get('task', 'Unknown')} | Tools: {tool_names} | Args: {args_str}"
        
        risk_level = classify_action(step_desc, tool_guessed)

    state['risk_level'] = risk_level
    color = "green" if risk_level == "SAFE" else "yellow" if risk_level == "MODERATE" else "red"
    console.print(f"[bold {color}]🛡️  Risk level: {risk_level}[/bold {color}]")
    
    # Store pending info
    action_type = _get_action_type_from_step(step_desc, tool_guessed)
    state['pending_approval'] = {
        "step_desc": step_desc,
        "tool_name": tool_guessed,
        "action_type": action_type
    }
    
    # Pre-check for auto-approval to satisfy router requirements
    pref = preference_manager.get_preference(action_type)
    if pref == "NEVER_ASK":
        state['approval_granted'] = True
    elif pref == "AUTO" and risk_level in ["SAFE", "MODERATE"]:
        state['approval_granted'] = True
    else:
        state['approval_granted'] = False
        
    return state

def approval_request_node(state: AgentState) -> AgentState:
    """Pauses execution and asks user for approval."""
    risk_level = state.get('risk_level', 'SAFE')
    
    pending = state.get('pending_approval', {})
    step_desc = pending.get('step_desc', 'Unknown')
    action_type = pending.get('action_type', 'unknown')
    
    pref = preference_manager.get_preference(action_type)
    
    code_content = ""
    messages = state.get('messages', [])
    if messages:
        last_msg = messages[-1]
        if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
            for tc in last_msg.tool_calls:
                if tc.get("name") in ["python_executor", "file_writer"]:
                    code_content = tc.get("args", {}).get("code", tc.get("args", {}).get("content", ""))
                    break

    color = "red" if risk_level == "CRITICAL" else "yellow"

    prompt_text = (
        f"[bold]Action:[/bold] {step_desc}\n"
        f"[bold]Type:[/bold] {action_type}\n"
        f"[bold]Risk Level:[/bold] [{color}]{risk_level}[/{color}]"
    )
    
    console.print(Panel(prompt_text, title="⚠️  APPROVAL REQUIRED", border_style=color))
    
    if code_content:
        console.print("[bold]Code Preview:[/bold]")
        syntax = Syntax(code_content, "python" if action_type == "python_executor" else "text", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, border_style="grey50"))
    
    while True:
        try:
            agent_status.stop()
            decision = input("Approve this action? (yes/no): ").strip().lower()
            agent_status.start()
            
            if decision in ['yes', 'y']:
                state['approval_granted'] = True
                user_decision = "APPROVED"
                break
            elif decision in ['no', 'n']:
                state['approval_granted'] = False
                user_decision = "REJECTED"
                break
            else:
                agent_status.stop()
                print("Please answer 'yes' or 'no'.")
                agent_status.start()
        except KeyboardInterrupt:
            agent_status.start() # Ensure it's started back if caught or just leave to main
            state['approval_granted'] = False
            user_decision = "REJECTED"
            break
            
    approval_logger.log_approval(
        step_description=step_desc,
        action_type=action_type,
        risk_level=risk_level,
        user_decision=user_decision
    )
    
    # Store to session history list
    if 'approval_history' not in state:
        state['approval_history'] = []
    
    state['approval_history'].append({
        "step": step_desc,
        "decision": user_decision,
        "timestamp": datetime.now().isoformat()
    })
    
    return state

def approval_decision_node(state: AgentState) -> AgentState:
    """Processes user response and routes accordingly."""
    if state.get('approval_granted'):
        return state
        
    # Rejection processing
    console.print("\n[bold red]❌ Action rejected by user[/bold red]")
    
    if state.get('complexity') == 'COMPLEX':
        state['skip_current_step'] = True
        state['step_results'].append("[SKIPPED - User rejected critical action]")
    else:
        # For simple path rejection, the easiest clean way to break the loop
        # is to set a custom flag that the router can read to exit to END
        state['skip_current_step'] = True
        
        # Intercept rejection for SIMPLE by creating a ToolMessage with an error
        messages = state.get("messages", [])
        if messages:
            last_msg = messages[-1]
            if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                # Need to simulate the tool returns an error
                for tool_call in last_msg.tool_calls:
                    reject_msg = ToolMessage(
                        content="Error: User rejected the use of this tool. Do not try this action again.",
                        tool_call_id=tool_call["id"],
                        name=tool_call["name"]
                    )
                    messages.append(reject_msg)
        state['messages'] = messages

    return state


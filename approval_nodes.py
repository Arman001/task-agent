from langchain_core.messages import ToolMessage
from datetime import datetime

from state import AgentState
from risk_classifier import classify_action
from preference_manager import preference_manager
from approval_logger import approval_logger

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
            tool_guessed = next((t for t in ["file_writer", "file_reader", "web_search", "calculator", "http_request"] if t in step_desc), "")
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
                    if t in ["file_writer", "http_request", "url_fetch"]:
                        tool_guessed = t
                        break
                
                args_str = " | ".join([str(tc.get('args', {})) for tc in last_msg.tool_calls])
                step_desc = f"Task: {state.get('task', 'Unknown')} | Tools: {tool_names} | Args: {args_str}"
        
        risk_level = classify_action(step_desc, tool_guessed)

    state['risk_level'] = risk_level
    print(f"🛡️  Risk level: {risk_level}")
    
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
    
    # Default behavior if AUTO but we got here, or ALWAYS_ASK / CRITICAL
    print("\n⚠️  Approval Required")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Action: {step_desc}")
    print(f"Type: {action_type}")
    print(f"Risk Level: {risk_level}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    while True:
        try:
            decision = input("Approve this action? (yes/no): ").strip().lower()
            if decision in ['yes', 'y']:
                state['approval_granted'] = True
                user_decision = "APPROVED"
                break
            elif decision in ['no', 'n']:
                state['approval_granted'] = False
                user_decision = "REJECTED"
                break
            else:
                print("Please answer 'yes' or 'no'.")
        except KeyboardInterrupt:
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
    print("\n❌ Action rejected by user")
    
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


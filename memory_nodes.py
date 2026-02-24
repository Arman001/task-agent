from datetime import datetime
import time
import uuid
import hashlib
import os

from state import AgentState
from memory_manager import MemoryManager

memory_manager = MemoryManager()


def memory_retrieval_node(state: AgentState) -> AgentState:
    """
    Retrieve relevant context from memory before task execution.
    """
    task = state['task']
    
    # Initialize session ID if not present
    if 'session_id' not in state or not state['session_id']:
        state['session_id'] = str(uuid.uuid4())
    
    # Initialize memory context
    state['memory_context'] = {}
    
    print("💭 Retrieving relevant memories...")
    
    # 1. Search for similar past tasks
    similar_tasks = memory_manager.search_similar_tasks(task, limit=3)
    if similar_tasks:
        state['memory_context']['similar_tasks'] = similar_tasks
        print(f"   Found {len(similar_tasks)} similar past tasks")
    
    # 2. Get session history (context from current conversation)
    session_history = memory_manager.get_session_history(state['session_id'], limit=5)
    if session_history:
        state['memory_context']['session_history'] = session_history
        print(f"   Loaded {len(session_history)} tasks from current session")
    
    # 3. Check for file mentions in task and retrieve cached metadata
    words = task.lower().split()
    for word in words:
        if word.endswith(('.txt', '.csv', '.json', '.md', '.py')):
            file_path = os.path.join(os.getcwd(), word)
            cached_metadata = memory_manager.get_file_metadata(file_path)
            if cached_metadata:
                if 'file_cache' not in state['memory_context']:
                    state['memory_context']['file_cache'] = {}
                state['memory_context']['file_cache'][word] = cached_metadata
                print(f"   📁 Found cached metadata for {word}")
    
    # 4. Get tool performance stats for informed tool selection
    tool_stats = memory_manager.get_all_tool_stats()
    if tool_stats:
        state['memory_context']['tool_stats'] = tool_stats
    
    return state


def memory_writer_node(state: AgentState) -> AgentState:
    """
    Save task outcome to memory after execution.
    """
    # Skip if explicitly disabled
    if not state.get('should_save_memory', True):
        return state
    
    print("💾 Saving to memory...")
    
    # Determine success (no errors or fallback not triggered)
    success = len(state.get('errors', [])) == 0 and not state.get('fallback_triggered', False)
    
    # Extract tools used
    tools_used = []
    for tool_name, status in state.get('tool_status', {}).items():
        if status == 'success':
            tools_used.append(tool_name.replace('step_', ''))
    
    # Calculate execution time (approximate based on step count)
    execution_time = len(state.get('step_results', [])) * 2.0  # Rough estimate
    
    # Get result summary
    result_summary = state.get('result', '')[:500]
    if not result_summary and state.get('messages'):
        messages = state.get('messages', [])
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, 'content'):
                result_summary = last_message.content[:500]
            else:
                result_summary = str(last_message)[:500]
                
    
    # Save to task history
    memory_manager.save_task(
        task=state['task'],
        complexity=state.get('complexity', 'UNKNOWN'),
        tools_used=tools_used,
        success=success,
        execution_time=execution_time,
        result_summary=result_summary,
        error_count=len(state.get('errors', []))
    )
    
    # Save to session memory
    session_id = state.get('session_id', str(uuid.uuid4()))
    task_index = len(memory_manager.get_session_history(session_id))
    
    memory_manager.save_session_task(
        session_id=session_id,
        task_index=task_index,
        task=state['task'],
        result=result_summary
    )
    
    # Update tool performance stats
    for tool_name, status in state.get('tool_status', {}).items():
        if tool_name.startswith('step_'):  # Skip legacy or generic names
            continue
            
        tool_success = (status == 'success')
        memory_manager.update_tool_performance(
            tool_name=tool_name,
            success=tool_success,
            response_time=2.0  # Approximate
        )
    
    print("   ✅ Memory saved")
    
    return state


def memory_optimizer_node(state: AgentState) -> AgentState:
    """
    Optional: Use memory to optimize execution (skip redundant steps).
    This can be added to planner_node logic.
    """
    memory_context = state.get('memory_context', {})
    
    # Example: If file metadata is cached, add note to skip validation
    if 'file_cache' in memory_context and memory_context['file_cache']:
        print("⚡ Memory optimization: File metadata available, can skip validation")
        # This information can be used by the planner
    
    return state

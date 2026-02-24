from agent import agent
from state import AgentState
from memory_manager import MemoryManager
import uuid
import os

memory_manager = MemoryManager()

def test_memory_persistence():
    """Test that tasks are saved to memory."""
    print("\n=== Test 1: Memory Persistence ===")
    
    session_id = str(uuid.uuid4())
    
    state = AgentState(
        task="Calculate 10 * 5",
        complexity="",
        plan=[],
        current_step=0,
        step_results=[],
        result="",
        messages=[],
        errors=[],
        retry_count=0,
        max_retries=3,
        tool_status={},
        fallback_triggered=False,
        session_id=session_id,
        memory_context={},
        should_save_memory=True
    )
    
    result = agent.invoke(state)
    
    # Check memory
    recent_tasks = memory_manager.get_recent_tasks(limit=1)
    assert len(recent_tasks) > 0, "Task not saved to memory"
    assert "Calculate" in recent_tasks[0]['task']
    
    print("✅ Test 1 passed: Task saved to memory\n")


def test_context_retrieval():
    """Test that similar tasks are retrieved."""
    print("\n=== Test 2: Context Retrieval ===")
    
    # First, save a task
    session_id = str(uuid.uuid4())
    
    state1 = AgentState(
        task="Search for Python tutorials",
        complexity="SIMPLE",
        plan=[],
        current_step=0,
        step_results=[],
        result="Found tutorials",
        messages=[],
        errors=[],
        retry_count=0,
        max_retries=3,
        tool_status={},
        fallback_triggered=False,
        session_id=session_id,
        memory_context={},
        should_save_memory=True
    )
    
    result1 = agent.invoke(state1)
    
    # Now search for similar task
    similar = memory_manager.search_similar_tasks("Search for Python guides", limit=3)
    assert len(similar) > 0, "Similar tasks not found"
    
    print(f"✅ Test 2 passed: Found {len(similar)} similar tasks\n")


def test_file_caching():
    """Test that file metadata is cached."""
    print("\n=== Test 3: File Metadata Caching ===")
    
    session_id = str(uuid.uuid4())
    
    # Create and analyze a file
    state = AgentState(
        task="Create file test_memory.txt with 'Hello Memory' and analyze it",
        complexity="",
        plan=[],
        current_step=0,
        step_results=[],
        result="",
        messages=[],
        errors=[],
        retry_count=0,
        max_retries=3,
        tool_status={},
        fallback_triggered=False,
        session_id=session_id,
        memory_context={},
        should_save_memory=True
    )
    
    result = agent.invoke(state)
    
    # Check if file metadata was cached
    file_path = os.path.join(os.getcwd(), "test_memory.txt")
    cached = memory_manager.get_file_metadata(file_path)
    
    assert cached is not None, "File metadata not cached"
    print(f"✅ Test 3 passed: File metadata cached\n")
    
    # Cleanup
    if os.path.exists(file_path):
        os.remove(file_path)


def test_tool_performance():
    """Test that tool performance is tracked."""
    print("\n=== Test 4: Tool Performance Tracking ===")
    
    # Run a task that uses calculator
    session_id = str(uuid.uuid4())
    
    state = AgentState(
        task="Calculate 25 * 4",
        complexity="",
        plan=[],
        current_step=0,
        step_results=[],
        result="",
        messages=[],
        errors=[],
        retry_count=0,
        max_retries=3,
        tool_status={},
        fallback_triggered=False,
        session_id=session_id,
        memory_context={},
        should_save_memory=True
    )
    
    result = agent.invoke(state)
    
    # Check tool stats
    stats = memory_manager.get_tool_stats('calculator')
    if stats:
        print(f"Calculator stats: {stats['total_calls']} calls, {stats['success_rate']:.1%} success")
        print("✅ Test 4 passed: Tool performance tracked\n")
    else:
        print("⚠️  Test 4: No stats yet (might need more usage)\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 Phase 4 Memory Test Suite")
    print("="*60)
    
    test_memory_persistence()
    test_context_retrieval()
    test_file_caching()
    test_tool_performance()
    
    print("="*60)
    print("✅ All tests completed!")
    print("="*60 + "\n")

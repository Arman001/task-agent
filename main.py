from agent import agent
from state import AgentState
from memory_manager import MemoryManager
import uuid

memory_manager = MemoryManager()

def run_agent(task: str, session_id: str):
    print(f"\n{'='*60}")
    print(f"📋 Task: {task}")
    print(f"{'='*60}\n")

    initial_state = AgentState(
        task=task,
        complexity="",
        plan=[],
        current_step=0,
        step_results=[],
        result="",
        messages=[],
        # Phase 3 fields
        errors=[],
        retry_count=0,
        max_retries=3,
        tool_status={},
        fallback_triggered=False,
        # Phase 4 fields
        session_id=session_id,
        memory_context={},
        should_save_memory=True
    )

    print("🤔 Agent is analyzing...\n")
    final_state = agent.invoke(initial_state)

    print(f"{'='*60}")
    print("✅ Final Result:")
    print(f"{'='*60}")

    if final_state.get("result"):
        print(f"\n{final_state['result']}\n")
    else:
        messages = final_state.get("messages", [])
        if messages:
            last = messages[-1]
            print(f"\n{getattr(last, 'content', last)}\n")

    # Show memory context if available
    memory_ctx = final_state.get('memory_context', {})
    if memory_ctx.get('similar_tasks'):
        print(f"💭 Used context from {len(memory_ctx['similar_tasks'])} similar past tasks")

    print(f"{'='*60}\n")


def show_memory_stats():
    """Display memory statistics."""
    print("\n" + "="*60)
    print("📊 Memory Statistics")
    print("="*60)
    
    stats = memory_manager.get_memory_stats()
    
    print(f"\nTotal tasks executed: {stats['total_tasks']}")
    print(f"Successful tasks: {stats['successful_tasks']}")
    print(f"Success rate: {stats['success_rate']:.1%}")
    print(f"Cached files: {stats['cached_files']}")
    print(f"Tracked tools: {stats['tracked_tools']}")
    
    # Show tool performance
    print("\n📈 Tool Performance:")
    tool_stats = memory_manager.get_all_tool_stats()
    for tool in tool_stats[:5]:  # Top 5
        print(f"  • {tool['tool_name']}: {tool['success_rate']:.1%} success ({tool['total_calls']} calls)")
    
    print("\n" + "="*60 + "\n")


def clear_memory():
    """Clear all memory."""
    confirm = input("⚠️  Clear all memory? This cannot be undone. (yes/no): ")
    if confirm.lower() == 'yes':
        memory_manager.clear_all_memory()
        print("✅ Memory cleared\n")
    else:
        print("❌ Cancelled\n")


def main():
    # Generate session ID for this run
    session_id = str(uuid.uuid4())
    
    print("\n" + "=" * 60)
    print("🤖 Task Automation Agent - Phase 4")
    print("Simple tasks: Direct execution")
    print("Complex tasks: Planning + Step execution")
    print("Memory: Learns from every task")
    print("=" * 60)

    print("\n📝 Try these examples:")
    print("Simple: 'Calculate 15 * 8'")
    print("Simple: 'What's the weather in London?'")
    print("Simple: 'Search for AI agents'")
    print("Complex: 'Create a test file with hello world and analyze it'")
    print("\n🔧 Commands:")
    print("'stats' - Show memory statistics")
    print("'clear' - Clear all memory")
    print("'exit' or 'quit' - Stop\n")

    while True:
        try:
            task = input("👤 Enter your task: ").rstrip()
            if task.lower() in {"exit", "quit", "q"}:
                print("\n👋 Goodbye!\n")
                break
            
            if task.lower() == 'stats':
                show_memory_stats()
                continue
            
            if task.lower() == 'clear':
                clear_memory()
                continue
            
            if task:
                run_agent(task, session_id)
        except KeyboardInterrupt:
            print("\n👋 Goodbye!\n")
            break


if __name__ == "__main__":
    main()

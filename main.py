from src.core.agent import agent
from src.core.state import AgentState
from src.memory.manager import MemoryManager
from src.approval.preferences import preference_manager
from src.approval.logger import approval_logger
from datetime import datetime
import uuid
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from src.core.ui import console, agent_status

memory_manager = MemoryManager()

def run_agent(task: str, session_id: str):
    console.print(Panel(f"[bold white]{task}[/bold white]", title="📋 Task", border_style="blue"))

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
        should_save_memory=True,
        # Phase 5 fields
        pending_approval={},
        approval_granted=False,
        approval_history=[],
        user_preferences={},
        risk_level="SAFE",
        skip_current_step=False,
        # Phase 6 fields
        code_executions=[],
        code_to_execute="",
        execution_output="",
        generated_files=[]
    )

    agent_status.start()
    try:
        final_state = agent.invoke(initial_state)
    finally:
        agent_status.stop()

    if final_state.get("result"):
        result_text = final_state['result']
    else:
        messages = final_state.get("messages", [])
        if messages:
            last = messages[-1]
            result_text = getattr(last, 'content', str(last))
        else:
            result_text = "No output."

    console.print(Panel(result_text, title="✅ Final Result", border_style="green"))

    # Show memory context if available
    memory_ctx = final_state.get('memory_context', {})
    if memory_ctx.get('similar_tasks'):
        console.print(f"[purple]💭 Used context from {len(memory_ctx['similar_tasks'])} similar past tasks[/purple]\n")


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

def show_rules():
    print("\n" + "="*60)
    print("🛡️  Approval Preferences")
    print("="*60)
    prefs = preference_manager.get_all_preferences()
    for act, pol in prefs.items():
        print(f"  • {act}: {pol}")
    print("="*60 + "\n")

def config_approvals():
    print("\n" + "="*60)
    print("⚙️  Configure Approvals")
    print("="*60)
    prefs = preference_manager.get_all_preferences()
    for act, pol in prefs.items():
        val = input(f"Preference for {act} (current: {pol}) [ALWAYS_ASK/NEVER_ASK/AUTO/skip/quit]: ").strip().upper()
        if val in ["QUIT", "EXIT", "Q"]:
            print("🛑 Exiting configuration.")
            break
        elif val in ["ALWAYS_ASK", "NEVER_ASK", "AUTO"]:
            preference_manager.set_preference(act, val)
            print(f"✅ Updated {act} to {val}")
        elif val and val != "SKIP":
            print("❌ Invalid input, keeping unchanged.")
    print("="*60 + "\n")

def show_approval_history():
    print("\n" + "="*60)
    print("📖 Approval History")
    print("="*60)
    history = approval_logger.get_recent_approvals()
    for item in history:
        print(f"  • [{item['timestamp']}] {item['action_type']} ({item['risk_level']}) - Decision: {item['user_decision']}")
    
    stats = approval_logger.get_approval_stats()
    print(f"\nStats: {stats.get('APPROVED', 0)} Approved | {stats.get('REJECTED', 0)} Rejected")
    print("="*60 + "\n")

def show_code_history():
    print("\n" + "="*60)
    console.print(Panel("[bold]📖 Code Execution History[/bold]", border_style="cyan"))
    
    executions = memory_manager.get_code_executions(limit=5)
    if not executions:
        console.print("No code executions found.")
        print("="*60 + "\n")
        return
        
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Timestamp", style="dim")
    table.add_column("Status")
    table.add_column("Files Generated")
    
    for ex in executions:
        status_str = "[green]✅ Success[/green]" if ex['success'] else "[red]❌ Failed[/red]"
        files_str = ", ".join(ex['generated_files']) if ex['generated_files'] else "-"
        try:
            dt = datetime.fromisoformat(ex['timestamp'])
            time_str = dt.strftime("%I:%M %p")
        except:
            time_str = ex['timestamp'][:16]
            
        table.add_row(time_str, status_str, files_str)
        
    console.print(table)
    print("="*60 + "\n")

def main():
    # Generate session ID for this run
    session_id = str(uuid.uuid4())
    
    welcome_panel = Panel(
        "[bold cyan]Simple tasks:[/bold cyan] Direct execution\n"
        "[bold cyan]Complex tasks:[/bold cyan] Planning + Step execution\n"
        "[bold cyan]Memory:[/bold cyan] Learns from every task\n"
        "[bold cyan]Safety:[/bold cyan] Human-in-the-loop approvals\n"
        "[bold cyan]Analysis:[/bold cyan] Code Execution & Rich UI",
        title="🤖 Task Automation Agent - Phase 6",
        border_style="cyan"
    )
    console.print(welcome_panel)

    print("\n📝 Try these examples:")
    print("Simple: 'Calculate 15 * 8'")
    print("Simple: 'What's the weather in London?'")
    print("Simple: 'Search for AI agents'")
    print("Complex: 'Create a test file with hello world and analyze it'")
    print("\n🔧 Commands:")
    print("'stats' - Show memory statistics")
    print("'clear' - Clear all memory")
    print("'show-rules' - Display current approval preferences")
    print("'config-approvals' - Interactive preference configuration")
    print("'approval-history' - Show recent approval decisions")
    print("'show-code-history' - Display recent code executions")
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
                
            if task.lower() == 'show-rules':
                show_rules()
                continue
                
            if task.lower() == 'config-approvals':
                config_approvals()
                continue
                
            if task.lower() == 'approval-history':
                show_approval_history()
                continue
            
            if task.lower() == 'show-code-history':
                show_code_history()
                continue
            
            if task:
                run_agent(task, session_id)
        except KeyboardInterrupt:
            print("\n👋 Goodbye!\n")
            break


if __name__ == "__main__":
    main()

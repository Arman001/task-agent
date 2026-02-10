from agent import agent
from state import AgentState


def run_agent(task: str):
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
        fallback_triggered=False
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

    print(f"{'='*60}\n")


def main():
    print("\n" + "=" * 60)
    print("🤖 Task Automation Agent - Phase 3")
    print("Simple tasks: Direct execution")
    print("Complex tasks: Planning + Step execution")
    print("NEW: Web search, API calls, Error handling & Retry")
    print("=" * 60)

    print("\n📝 Try these examples:")
    print("Simple: 'Calculate 15 * 8'")
    print("Simple: 'What's the weather in London?'")
    print("Simple: 'Search for AI agents'")
    print("Complex: 'Search for Python tutorials and summarize findings'")
    print("Complex: 'Create a test file with hello world and analyze it'")
    print()

    while True:
        try:
            task = input("👤 Enter your task: ").rstrip()
            if task.lower() in {"exit", "quit", "q"}:
                print("\n👋 Goodbye!\n")
                break
            if task:
                run_agent(task)
        except KeyboardInterrupt:
            print("\n👋 Goodbye!\n")
            break


if __name__ == "__main__":
    main()

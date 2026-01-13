from agent import agent
from state import AgentState


def run_agent(task: str):
    """
    Runs the agent with a given task.
    
    Args:
        task: The task description from the user
    """
    print(f"\n{'='*60}")
    print(f"📋 Task: {task}")
    print(f"{'='*60}\n")
    
    # For simple math, try direct calculation first
    if any(op in task.lower() for op in ['add', 'plus', '+']) and any(num in task for num in '0123456789'):
        try:
            # Extract numbers for simple addition
            import re
            numbers = re.findall(r'\d+', task)
            if len(numbers) >= 2:
                result = sum(int(num) for num in numbers)
                print(f"✅ Quick calculation: {' + '.join(numbers)} = {result}\n")
                return
        except:
            pass
    
    # For text summarization, provide a simple fallback
    if "summarize" in task.lower() and '"' in task:
        try:
            import re
            quoted_text = re.findall(r'"([^"]+)"', task)
            if quoted_text:
                text = quoted_text[0]
                words = text.split()
                if len(words) > 20:
                    # Simple summary: first sentence + key info
                    sentences = text.split('. ')
                    summary = f"Summary: {sentences[0]}. The text contains {len(words)} words and discusses {len(sentences)} main points."
                    print(f"✅ Quick Summary:\n{summary}\n")
                    return
        except:
            pass
    
    # Initialize state
    initial_state = AgentState(
        task=task,
        action="",
        result="",
        messages=[]
    )
    
    try:
        # Run the agent
        print("🤔 Agent is thinking...\n")
        final_state = agent.invoke(initial_state)
        
        # Extract and display results
        print(f"{'='*60}")
        print("✅ Result:")
        print(f"{'='*60}")
        
        # Get the final result
        if final_state.get("result"):
            print(f"\n{final_state['result']}\n")
        else:
            # Get from messages
            messages = final_state.get("messages", [])
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, 'content'):
                    print(f"\n{last_message.content}\n")
                else:
                    print(f"\n{last_message}\n")
        
        print(f"{'='*60}\n")
        
    except Exception as e:
        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            print(f"\n⚠️  API Quota Exceeded: You've hit the free tier limits.")
            print(f"💡 Solutions:")
            print(f"   • Wait 10-15 minutes before trying again")
            print(f"   • Upgrade to a paid Gemini API plan")
            print(f"   • Use fewer requests per minute\n")
        else:
            print(f"\n❌ Error: {str(e)}\n")


def main():
    """
    Main CLI loop for interacting with the agent.
    """
    print("\n" + "="*60)
    print("🤖 Task Automation Agent - Phase 1")
    print("="*60)
    print("\nWelcome! I can help you with:")
    print("  • Mathematical calculations")
    print("  • Text analysis")
    print("  • Answering questions")
    print("\nType 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            # Get user input
            task = input("👤 Enter your task: ").strip()
            
            # Check for exit commands
            if task.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!\n")
                break
            
            # Skip empty inputs
            if not task:
                continue
            
            # Run the agent
            run_agent(task)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}\n")


if __name__ == "__main__":
    main()
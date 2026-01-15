from agent import agent

# Generate and save the workflow diagram
graph = agent.get_graph()

try:
    png_data = graph.draw_mermaid_png()
    with open("agent_workflow.png", "wb") as f:
        f.write(png_data)
    print("✅ Workflow diagram saved as 'agent_workflow.png'")
except Exception as e:
    print(f"❌ Error generating diagram: {e}")
    print("\nTry installing: pip install pygraphviz or pip install grandalf")

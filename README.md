# 🤖 Task Automation Agent (Phase 2)

A step-by-step, build-in-public project focused on creating a **real task automation agent** using modern agentic tooling.

This repository documents the **incremental evolution** of an AI agent — starting from a minimal, working core and gradually adding planning, tools, memory, and control mechanisms.

> Motto: **AI For Everyone**

---

## 🎯 Project Goal

Most "AI agent" demos stop at prompts.

This project focuses on **inspectable, extensible systems** that:
- Maintain explicit state
- Make decisions instead of hardcoded branching
- Use real tools
- Evolve incrementally without rewrites

Each phase adds **one clear capability**, while keeping the system runnable and understandable.

---

## 🧩 Current Phase: Phase 2 – Multi-Step Planning Agent

### What Phase 2 adds

Phase 2 transforms the agent from single-step decision making to **intelligent multi-step planning**:

- **Automatic complexity detection**: LLM analyzes tasks and routes appropriately
- **Multi-step planning**: Complex tasks broken into sequential steps
- **Step-by-step execution**: Each step builds on previous results
- **File system operations**: Real-world workflow capabilities
- **Backward compatibility**: Simple tasks still use Phase 1 direct execution

### 🔄 How it works

**Two execution paths**:

```
Simple Task → Analyzer → "SIMPLE" → Direct Execution → Result
Complex Task → Analyzer → "COMPLEX" → Planner → Step Execution → Result
```

**Example flows**:
- `"Calculate 15 * 8"` → Direct calculator usage
- `"Create a report from data.txt"` → 4-step plan: check file → read → analyze → write report

---

## ✅ Phase 2 Capabilities

- **Intelligent routing**: LLM decides between simple and complex execution
- **Multi-step planning**: Complex tasks decomposed automatically
- **Context preservation**: Each step sees previous results
- **File operations**: Read, write, and check files
- **Progress tracking**: Clear step-by-step execution feedback
- **Tool integration**: Calculator, text analysis, file system
- **CLI interface**: Enhanced with planning indicators

---

## 🏗 Phase 2 Architecture

```
User Input
    ↓
Complexity Analyzer (LLM)
    ↓
┌─ SIMPLE ────────────┐    ┌─ COMPLEX ─────────────┐
│ Simple Agent        │    │ Planner               │
│ ↓                   │    │ ↓                     │
│ Tools (if needed)   │    │ Executor Loop         │
│ ↓                   │    │ ↓                     │
│ Direct Result       │    │ Coordinator           │
└─────────────────────┘    └───────────────────────┘
                ↓
            Final Output
```

**6 LangGraph Nodes**:
- `analyzer`: Determines task complexity
- `planner`: Creates step-by-step plans
- `executor`: Executes individual steps
- `coordinator`: Compiles final results
- `simple_agent`: Handles direct execution (Phase 1 behavior)
- `tools`: Calculator, text analyzer, file operations

---

## 🛠 Tech Stack

- **LangGraph** – Agent flow, state, and routing
- **LangChain** – Tool abstractions
- **Groq (Llama 3.1 8B Instant)** – Fast, reliable LLM reasoning
- **Python** – Core implementation
- **dotenv** – Environment configuration

---

## 📁 Project Structure

```
.
├── agent.py                    # Phase 2 agent with planning nodes
├── tools.py                    # Tools (calculator, text analyzer, file ops)
├── state.py                    # Enhanced state with planning fields
├── main.py                     # CLI with Phase 2 interface
├── visualize_graph.py          # Generate workflow diagram
├── agent_workflow.png          # Visual representation of agent flow
├── sample_data.txt             # Test file for complex workflows
└── README.md
```

---

## 🚀 Running the Agent

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set environment variables
Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

**Get your free Groq API key**:
1. Visit [https://console.groq.com/](https://console.groq.com/)
2. Sign up for free account
3. Generate API key
4. Add to `.env` file

### 3. Run
```bash
python main.py
```

### 4. Try these examples:

**Simple tasks** (direct execution):
- `Calculate 25 * 16`
- `What is artificial intelligence?`

**Complex tasks** (multi-step planning):
- `Create a test file with hello world and analyze it`
- `Read sample_data.txt and create a summary report`

---

## 📊 Phase Evolution

### ✅ Phase 1 (Branch: `phase-1`)
- Basic decision-making agent
- Tool usage (calculator, text analyzer)
- Simple state management
- Direct task execution

### ✅ Phase 2 (Branch: `main`)
- **NEW**: Automatic complexity detection
- **NEW**: Multi-step planning and execution
- **NEW**: File system operations
- **NEW**: Context preservation across steps
- **ENHANCED**: Intelligent routing
- **MAINTAINED**: Phase 1 compatibility for simple tasks

---

## 🧠 Why This Architecture?

LangGraph enables:

- **Explicit state transitions**: No hidden control logic
- **Deterministic routing**: Clear decision points
- **Inspectable behavior**: Every step is visible
- **Incremental evolution**: Add capabilities without rewrites
- **Backward compatibility**: Previous phases continue working

This project treats agents as **software systems**, not prompt tricks.

---

## 🔮 Roadmap

Planned future phases:

- **Phase 3**: Real-world tool integrations (APIs, workflows, databases)
- **Phase 4**: Failure detection & recovery strategies
- **Phase 5**: Memory and historical context
- **Phase 6**: Feedback loops and human-in-the-loop control

Each phase builds incrementally without breaking previous functionality.

---

## 🤝 Use Cases

This architecture is suitable for:

- **Task automation systems**: Multi-step workflow execution
- **AI-assisted workflows**: Intelligent task decomposition
- **Controlled agent execution**: Transparent decision making
- **Client-facing automation tools**: Reliable multi-step processing
- **Educational agent experiments**: Clear, inspectable architecture

---

## 📢 Build in Public

This project is intentionally developed in public to:

- Encourage learning through transparency
- Share real implementation patterns
- Avoid agent hype and black-box behavior
- Demonstrate incremental system evolution

Feedback, ideas, and discussion are welcome.

---

## 📜 License

MIT License — free to use, modify, and learn from.

---

## 👤 Author

**Muhammad Saad**  
AI • Automation • Agentic Systems  
Website: [https://muhammadsaad.dev](https://muhammadsaad.dev)

---

> "Good agents are not magical.  
> They are well-designed systems."

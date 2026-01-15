# 🤖 Task Automation Agent (Phase 1)

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

## 🧩 Phase 1 – Basic Task-Aware Agent (Current)

### What this phase does

Phase 1 implements a **minimal but real agent loop**:

- Accepts a natural language task
- Decides whether a tool is required
- Calls the appropriate tool when needed
- Returns a result based on execution
- Maintains structured state across steps

This phase focuses on **decision-making**, not autonomy hype.

---

### ✅ Capabilities

- Task understanding via LLM
- Explicit agent state using `TypedDict`
- Tool calling (calculator, text analysis)
- Decision routing with LangGraph
- Tool → agent feedback loop
- CLI interface for interaction

---

### ❌ What this phase intentionally does NOT include

- Multi-step planning
- Memory across runs
- Failure recovery
- Human approval loops
- External integrations (APIs, workflows)

These are added **incrementally in later phases**.

---

## 🏗 Architecture Overview

```
User Task
    ↓
Agent (LLM)
    ↓
Decision Router
├─→ Tool Execution
│       ↓
│   Tool Result
│       ↓
└── Agent (Reasoning)
    ↓
Final Output
```

The agent uses **LangGraph** to model this flow explicitly instead of relying on hidden control logic.

---

## 🛠 Tech Stack

- **LangGraph** – Agent flow, state, and routing
- **LangChain** – Tool abstractions
- **Gemini (Google Generative AI)** – LLM reasoning
- **Python** – Core implementation
- **dotenv** – Environment configuration

---

## 📁 Project Structure

```
.
├── agent.py          # Agent logic and LangGraph setup
├── tools.py          # Tool definitions (calculator, text analyzer)
├── state.py          # Agent state definition
├── main.py           # CLI entry point
├── .env.example      # Environment variable template
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
GOOGLE_API_KEY=your_api_key_here
```

### 3. Run
```bash
python main.py
```

You can then enter tasks such as:

- `Calculate (45 * 12) / 3`
- `Analyze this text: Hello world\nThis is a test`

---

## 🧠 Why LangGraph?

LangGraph allows:

- Explicit state transitions
- Deterministic control flow
- Inspectable agent behavior
- Easy extension for planning, memory, retries, and approvals

This project treats agents as **software systems**, not prompt tricks.

---

## 🔮 Roadmap

Planned future phases:

- **Phase 2**: Task planning & step decomposition
- **Phase 3**: Real-world tool integrations (APIs, workflows, files)
- **Phase 4**: Failure detection & recovery strategies
- **Phase 5**: Memory and historical context
- **Phase 6**: Feedback loops and human-in-the-loop control

Each phase will be added without breaking previous ones.

---

## 🤝 Use Cases

This architecture is suitable for:

- Task automation systems
- AI-assisted workflows
- Controlled agent execution
- Client-facing automation tools
- Educational agent experiments

---

## 📢 Build in Public

This project is intentionally developed in public to:

- Encourage learning through transparency
- Share real implementation patterns
- Avoid agent hype and black-box behavior

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

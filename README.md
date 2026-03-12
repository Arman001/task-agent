# 🤖 Task Automation Agent (Phase 6)

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

## 🧩 Current Phase: Phase 6 – Terminal UI & Rich Interactive Experience

### What Phase 6 adds

Phase 6 completely revamps the user interaction layer by introducing a powerful, interactive Terminal UI (TUI) powered by the `rich` Python library. It moves away from standard print statements to structured, visually appealing, and organized panel displays:

- **Rich Terminal UI**: Beautiful, organized panels for tasks, memory retrieval, agent execution, and results.
- **Dynamic Task Layouts**: Responsive formatting that auto-adjusts to terminal size for readability.
- **Color-Coded Feedback**: Instant visual cues for successful steps (Green), failures (Red), and intermediate reasoning (Yellow/Cyan).
- **Graceful Visual Loops**: Clear visual separation of the human-in-the-loop approval requests and their outcomes.
- **Backward compatibility**: All Phase 1-5 functionality (Memory, Fallbacks, Planners, Risk Classification, Approvals) sits powerfully underneath the new UI.

### 🔄 How it works

**Flow with Approvals**:

```
Input → Memory Retrieval → Analysis & Planning → Risk Classifier → Approval Node (If needed) → Execution → Result
```

**Approval Modes**:
1. **`NEVER_ASK`**: Executes silently without interrupting.
2. **`ALWAYS_ASK`**: Forces a pause and human terminal prompt no matter what.
3. **`AUTO` (Smart)**: Checks the Risk Classifier. Bypasses the prompt if `SAFE`/`MODERATE`, but stops for `CRITICAL` (e.g., dropping a file).

---

## ✅ Phase 6 Capabilities

- **Rich Visual Interface**: Organized tables, panels, and live status displays
- **Human-in-the-Loop**: Active intercepts for dangerous executions (Phase 5)
- **Granular Control**: User specific rule table mapping natively via `config-approvals` (Phase 5)
- **Intelligent caching**: File metadata speeds up checks and reads (Phase 4)
- **Tool learning**: Tracks success and failure rates per tool (Phase 4)
- **Conversation history**: Uses recent tasks for context (Phase 4)
- **Persistent storage**: Stores logs in local SQLite database (Phase 4)
- **Internet connectivity**: Search web, fetch URLs, call APIs (Phase 3)
- **Error resilience**: Automatic retry with exponential backoff (Phase 3)
- **Fallback intelligence**: Creates alternative plans when primary fails (Phase 3)

---

## 🏗 Phase 6 Architecture

```
User Input
    ↓
Memory Retrieval (Fetch Context)
    ↓
Complexity Analyzer (LLM)
    ↓
┌─ SIMPLE ────────────┐    ┌─ COMPLEX ─────────────────────┐
│ Simple Agent        │    │ Planner                       │
│ ↓                   │    │ ↓                             │
│ Risk Classifier     │    │ Risk Classifier Loop          │
│ ↓                   │    │ ↓                             │
│ Approval Required?  │←──→│ Approval Required?            │
│ ↓                   │    │ ↓                             │
│ Tools (if needed)   │    │ Executor Loop                 │
│ ↓                   │    │ ↓                             │
│ Direct Result       │    │ Error? → Retry (3x backoff)   │
└─────────┬───────────┘    │ ↓                             │
          │                │ Max Retries? → Fallback Plan  │
          │                │ ↓                             │
          │                │ Coordinator                   │
          │                └──────────────┬────────────────┘
          └─────────────┬─────────────────┘
                        ↓
            Memory Writer (Save Context)
                        ↓
                  Final Output
```

**13 LangGraph Nodes**:
- `memory_retrieval`: Pre-fetches task context, session history and file caches
- `analyzer`: Determines task complexity
- `planner`: Creates step-by-step plans
- `risk_classifier`: Grades danger payload of executing step
- `approval_request`: Pauses terminal loop to ask user for permission
- `approval_decision`: Conditionally steps execution forward or skips safely
- `executor`: Executes individual steps with error handling
- `error_handler`: Analyzes failures, decides retry/fallback
- `fallback_planner`: Creates alternative approaches
- `coordinator`: Compiles final results with error summary
- `simple_agent`: Handles direct execution (Phase 1 behavior)
- `tools`: 10 tools (calculator, files, web, APIs, file deleter)
- `memory_writer`: Saves execution results, states, and telemetry to SQLite

---

## 🛠 Tech Stack

- **LangGraph** – Agent flow, state, and routing
- **LangChain** – Tool abstractions
- **Groq (Llama 3.3 70B Versatile)** – Fast, reliable LLM reasoning
- **Tavily** – Web search API
- **OpenWeatherMap** – Weather data API
- **Python** – Core implementation
- **dotenv** – Environment configuration

---

## 📁 Project Structure

```
.
├── src/
│   ├── approval/               # Risk grading and user approval loops
│   │   ├── classifier.py       # Risk grading logic for actions
│   │   ├── logger.py           # SQL User Decision logger
│   │   ├── nodes.py            # LangGraph node controllers for Approvals
│   │   └── preferences.py      # SQLite rule interface
│   ├── core/                   # Agent orchestration
│   │   ├── agent.py            # Core LangGraph logic & Router mapping
│   │   ├── config.py           # Configuration and API keys
│   │   ├── state.py            # State tracking definition
│   │   └── ui.py               # Shared rich UI theme components
│   ├── memory/                 # Persistence and context
│   │   ├── manager.py          # SQLite database interaction layer
│   │   ├── nodes.py            # Memory retrieval and saving Graph nodes
│   │   └── schema.py           # SQLite schema building
│   └── tools/                  # LLM Tools
│       └── tools.py            # File, Web, API, and System tools
├── scripts/                    # Helper scripts
├── tests/                      # Test suite
├── main.py                     # CLI with Phase 6 TUI interface
├── pyproject.toml              # Dependency config (uv)
├── agent_memory.db             # Local SQLite database (ignored)
└── README.md
```

---

## 🚀 Running the Agent

### 1. Install dependencies
```bash
pip install -r requirements.txt
# or with uv:
uv sync
```

### 2. Set environment variables
Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

**Get your API keys**:
1. **Groq**: https://console.groq.com/ (free)
2. **Tavily**: https://tavily.com/ (free tier)
3. **OpenWeatherMap**: https://openweathermap.org/api (free tier)

### 3. Initialize Memory DB
```bash
python memory_schema.py
```

### 4. Important: Terminal Sizing

> ⚠️ **IMPORTANT NOTE FOR UI**: Because this phase uses the `rich` library for an advanced Terminal UI (TUI), **please maximize or significantly increase the size of your terminal window BEFORE running the agent**. If your terminal is too narrow, the rich formatted panels will wrap awkwardly and ruin the neat interface experience.

### 5. Run
```bash
python main.py
# or with uv:
uv run python main.py
```

### 5. Try these examples:

**Simple tasks** (direct execution):
- `Calculate 25 * 16`
- `Search for LangGraph documentation`
- `What's the weather in London?`

**Complex tasks** (multi-step planning):
- `Create a test file with hello world and analyze it`

**Memory specific tasks**:
- `stats` -> See memory status and tool performance
- Type a repeat task -> Watch it execute faster (File Cache)
- Reference a past item -> E.g., "Analyze the file from earlier"

**Approval specific tasks**:
- `show-rules` -> View current safety rules
- `config-approvals` -> Modify safety rules dynamically
- `approval-history` -> View local DB tracking history

---

## 📊 Phase Evolution

### ✅ Phase 1 (Branch: `phase-1`)
- Basic decision-making agent
- Tool usage (calculator, text analyzer)
- Simple state management
- Direct task execution

### ✅ Phase 2 (Branch: `phase-2`)
- Automatic complexity detection
- Multi-step planning and execution
- File system operations
- Context preservation across steps
- Intelligent routing

### ✅ Phase 3 (Branch: `phase-3`)
- Web search (Tavily API)
- HTTP requests to any REST API
- URL content fetching
- Weather API integration
- Error handling with retry logic
- Exponential backoff (1s, 2s, 4s)
- Fallback planning for failures

### ✅ Phase 4 (Branch: `phase-4`)
- Task History Database
- Session/Context memory awareness
- File metadata caching
- Faster execution times through caching

### ✅ Phase 5 (Branch: `phase-5`)
- Human-in-the-loop dynamic approvals
- Safe / Moderate / Critical risk classification mapping
- SQLite-backed preference engine rules (`ALWAYS_ASK`, `NEVER_ASK`, `AUTO`)
- SQLite-backed User decision logger
- Safe fallback trapping for looping simple agents via `END` graphs
- Command line utility modifiers (`show-rules`, `config-approvals`, `approval-history`)

### ✅ Phase 6 (Branch: `main`)
- **NEW**: Full `rich` powered Terminal UI (TUI)
- **NEW**: Structured visual components (Panels, Tables, Formatting)
- **NEW**: Live display separation of tasks, memory, execution, and outputs
- **NEW**: Clean exception formatting and layout auto-adjustment

---

## 🧠 Why This Architecture?

LangGraph enables:

- **Explicit state transitions**: No hidden control logic
- **Deterministic routing**: Clear decision points
- **Inspectable behavior**: Every step is visible
- **Incremental evolution**: Add capabilities without rewrites
- **Backward compatibility**: Previous phases continue working
- **Error resilience**: Production-ready failure handling

This project treats agents as **software systems**, not prompt tricks.

---

## 🔮 Roadmap

Planned future phases:

- **Phase 7**: Multi-agent collaboration
- **Phase 8**: Deep UI integration / Docker deployment

Each phase builds incrementally without breaking previous functionality.

---

## 🤝 Use Cases

This architecture is suitable for:

- **Production automation systems**: Resilient multi-step workflows
- **AI-assisted research**: Web search + analysis + reporting
- **API integration workflows**: Connect multiple services reliably
- **Weather-aware applications**: Real-time weather data processing
- **Controlled agent execution**: Transparent decision making with error handling
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

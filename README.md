# 🤖 Task Automation Agent (Phase 5)

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

## 🧩 Current Phase: Phase 5 – Human-in-the-Loop & Approval Layer

### What Phase 5 adds

Phase 5 introduces a robust safety net. By letting the agent classify its own actions based on risk, it can pause execution dynamically and ask for explicit human permission before doing anything destructive (like deleting files or making POST requests):

- **Risk Classifier**: Automatically analyzes active tools/tasks and grades them as `SAFE`, `MODERATE`, or `CRITICAL`.
- **Preference Manager**: A granular, tool-by-tool SQLite rule engine (`ALWAYS_ASK`, `NEVER_ASK`, `AUTO`).
- **Dynamic Interception**: LangGraph dynamically intercepts execution strings, spins up a terminal warning, and traps the response.
- **Graceful Rejection**: Safely escapes the fallback LLM loop entirely without hallucinating if a user types "no".
- **Approval Logging**: Every single decision the user makes is logged persistently.
- **Backward compatibility**: All Phase 1-4 functionality (Memory, Fallbacks, Planners) is entirely preserved.

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

## ✅ Phase 5 Capabilities

- **Human-in-the-Loop**: Active intercepts for dangerous executions
- **Granular Control**: User specific rule table mapping natively via `config-approvals`
- **Intelligent caching**: File metadata speeds up checks and reads (Phase 4)
- **Tool learning**: Tracks success and failure rates per tool (Phase 4)
- **Conversation history**: Uses recent tasks for context (Phase 4)
- **Persistent storage**: Stores logs in local SQLite database (Phase 4)
- **Internet connectivity**: Search web, fetch URLs, call APIs (Phase 3)
- **Error resilience**: Automatic retry with exponential backoff (Phase 3)
- **Fallback intelligence**: Creates alternative plans when primary fails (Phase 3)

---

## 🏗 Phase 5 Architecture

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
- **Groq (Llama 3.1 8B Instant)** – Fast, reliable LLM reasoning
- **Tavily** – Web search API
- **OpenWeatherMap** – Weather data API
- **Python** – Core implementation
- **dotenv** – Environment configuration

---

## 📁 Project Structure

```
.
├── agent.py                    # Core agent logic & Router mapping
├── tools.py                    # Tools (basic + web + API + Deleter)
├── state.py                    # State with error, memory, and approval tracking
├── config.py                   # Configuration and API keys
├── main.py                     # CLI with Phase 5 command interface
├── memory_manager.py           # SQLite database interaction layer
├── memory_nodes.py             # Memory retrieval and saving nodes
├── memory_schema.py            # SQLite schema building
├── risk_classifier.py          # Risk grading logic for inputs Action
├── approval_nodes.py           # 3 LangGraph node controllers for Approval loops
├── preference_manager.py       # SQL Rule interface
├── approval_logger.py          # SQL User Decision interface
├── test_phase5.py               # Test suite
├── agent_memory.db             # Local memory database
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

### 4. Run
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

### ✅ Phase 5 (Branch: `main`)
- **NEW**: Human-in-the-loop dynamic approvals
- **NEW**: Safe / Moderate / Critical risk classification mapping
- **NEW**: SQLite-backed preference engine rules (`ALWAYS_ASK`, `NEVER_ASK`, `AUTO`)
- **NEW**: SQLite-backed User decision logger
- **NEW**: Safe fallback trapping for looping simple agents via `END` graphs
- **NEW**: Command line utility modifiers (`show-rules`, `config-approvals`, `approval-history`)

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

- **Phase 6**: Multi-agent collaboration
- **Phase 7**: UI integration or Docker packaging

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

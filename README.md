# 🤖 Task Automation Agent (Phase 4)

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

## 🧩 Current Phase: Phase 4 – Memory & Context

### What Phase 4 adds

Phase 4 gives the agent memory - it can now remember past tasks, learn from failures, and optimize based on experience:

- **Task History**: Remembers all past executions with outcomes
- **Context Awareness**: Maintains conversation context within session
- **File Caching**: Skips re-validation of known files
- **Pattern Learning**: Tracks tool success rates and learns optimal approaches
- **Faster Execution**: Repeat tasks run 2-3x faster with cached context
- **Backward compatibility**: All Phase 3 functionality preserved

### 🔄 How it works

**Flow with Memory**:

```
Input → Memory Retrieval → Analysis → Execution → Memory Writer → Result
```

**Memory Types**:
1. **Conversation Memory** (Short-term): Current session context, cleared on restart
2. **Task History** (Long-term): All executed tasks, searchable for similar past tasks
3. **Pattern Learning** (Intelligence): Tool success rates, file metadata cache, optimization

---

## ✅ Phase 4 Capabilities

- **Intelligent caching**: File metadata speeds up checks and reads
- **Tool learning**: Tracks success and failure rates per tool
- **Conversation history**: Uses recent tasks for context
- **Persistent storage**: Stores logs in local SQLite database
- **Internet connectivity**: Search web, fetch URLs, call APIs (Phase 3)
- **Error resilience**: Automatic retry with exponential backoff (Phase 3)
- **Fallback intelligence**: Creates alternative plans when primary fails (Phase 3)

---

## 🏗 Phase 4 Architecture

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

**10 LangGraph Nodes**:
- `memory_retrieval`: Pre-fetches task context, session history and file caches
- `analyzer`: Determines task complexity
- `planner`: Creates step-by-step plans
- `executor`: Executes individual steps with error handling
- `error_handler`: Analyzes failures, decides retry/fallback
- `fallback_planner`: Creates alternative approaches
- `coordinator`: Compiles final results with error summary
- `simple_agent`: Handles direct execution (Phase 1 behavior)
- `tools`: 9 tools (calculator, files, web, APIs)
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
├── agent.py                    # Core agent logic
├── tools.py                    # Tools (basic + web + API)
├── state.py                    # State with error & memory tracking
├── config.py                   # Configuration and API keys
├── main.py                     # CLI with Memory interface
├── memory_manager.py           # SQLite database interaction layer
├── memory_nodes.py             # Memory retrieval and saving nodes
├── memory_schema.py            # SQLite schema
├── test_phase4.py              # Test suite
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

### ✅ Phase 4 (Branch: `main`)
- **NEW**: Task History Database
- **NEW**: Session/Context memory awareness
- **NEW**: File metadata caching
- **NEW**: Tool success rate analytics
- **NEW**: Faster execution times through caching

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

- **Phase 5**: Feedback loops and human-in-the-loop control
- **Phase 6**: Multi-agent collaboration

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

# 🤖 Task Automation Agent (Phase 3)

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

## 🧩 Current Phase: Phase 3 – Real-World Tool Integration & Error Handling

### What Phase 3 adds

Phase 3 transforms the agent from file-based operations to **internet-connected, resilient system**:

- **Web search**: Real-time internet search via Tavily API
- **HTTP requests**: Call any REST API (GET/POST)
- **URL fetching**: Extract text content from webpages
- **Weather API**: Live weather data integration
- **Error handling**: Automatic retry with exponential backoff
- **Fallback planning**: Alternative approaches when primary fails
- **Backward compatibility**: All Phase 2 functionality preserved

### 🔄 How it works

**Execution with error handling**:

```
Task → Analyzer → SIMPLE/COMPLEX
                      ↓
                  Executor → Success → Continue
                      ↓
                   Error → Retry (3x with backoff)
                      ↓
                Max Retries → Fallback Planner → Alternative Approach
```

**Example flows**:
- `"Search for AI agents"` → Web search → Results
- `"What's the weather in Paris?"` → Weather API → Current conditions
- `"API fails"` → Retry 3x → Fallback to web search → Success

---

## ✅ Phase 3 Capabilities

- **Internet connectivity**: Search web, fetch URLs, call APIs
- **Weather data**: Real-time weather from OpenWeatherMap
- **Error resilience**: Automatic retry with exponential backoff (1s, 2s, 4s)
- **Fallback intelligence**: Creates alternative plans when primary fails
- **Tool status tracking**: Monitor success/failure of each step
- **Error reporting**: Clear error summaries in final output
- **Production ready**: Handles network failures, timeouts, API errors
- **Phase 2 compatible**: All previous features still work

---

## 🏗 Phase 3 Architecture

```
User Input
    ↓
Complexity Analyzer (LLM)
    ↓
┌─ SIMPLE ────────────┐    ┌─ COMPLEX ─────────────────────┐
│ Simple Agent        │    │ Planner                       │
│ ↓                   │    │ ↓                             │
│ Tools (if needed)   │    │ Executor Loop                 │
│ ↓                   │    │ ↓                             │
│ Direct Result       │    │ Error? → Retry (3x backoff)   │
└─────────────────────┘    │ ↓                             │
                           │ Max Retries? → Fallback Plan  │
                           │ ↓                             │
                           │ Coordinator                   │
                           └───────────────────────────────┘
                ↓
            Final Output
```

**8 LangGraph Nodes**:
- `analyzer`: Determines task complexity
- `planner`: Creates step-by-step plans
- `executor`: Executes individual steps with error handling
- `error_handler`: Analyzes failures, decides retry/fallback
- `fallback_planner`: Creates alternative approaches
- `coordinator`: Compiles final results with error summary
- `simple_agent`: Handles direct execution (Phase 1 behavior)
- `tools`: 9 tools (calculator, files, web, APIs)

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
├── agent.py                    # Phase 3 agent with error handling
├── tools.py                    # 9 tools (basic + web + API)
├── state.py                    # State with error tracking
├── config.py                   # Configuration and API keys
├── main.py                     # CLI with Phase 3 interface
├── test_phase3.py              # Test suite
├── visualize_graph.py          # Generate workflow diagram
├── PHASE3_SETUP.md             # Setup guide
├── PHASE3_PLAN.md              # Implementation plan
├── sample_data.txt             # Test file for workflows
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

### 3. Run
```bash
python main.py
# or with uv:
uv run python main.py
```

### 4. Try these examples:

**Simple tasks** (direct execution):
- `Calculate 25 * 16`
- `Search for LangGraph documentation`
- `What's the weather in London?`

**Complex tasks** (multi-step planning):
- `Search for Python tutorials and summarize findings`
- `Create a test file with hello world and analyze it`
- `Get weather for Paris and create a report`

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

### ✅ Phase 3 (Branch: `main`)
- **NEW**: Web search (Tavily API)
- **NEW**: HTTP requests to any REST API
- **NEW**: URL content fetching
- **NEW**: Weather API integration
- **NEW**: Error handling with retry logic
- **NEW**: Exponential backoff (1s, 2s, 4s)
- **NEW**: Fallback planning for failures
- **NEW**: Tool status tracking
- **ENHANCED**: Error reporting in results
- **MAINTAINED**: Full backward compatibility

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

- **Phase 4**: Memory and historical context
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

# HomeFlow AI — Intelligent Home-Task Coordination Assistant
*Built for the Amazon Developer Hackathon*

HomeFlow AI is an AI-powered household coordination assistant that unifies household activities, reminders, routines, and simulated entry events through natural-language instructions. Instead of pretending to perform actions with mock text, HomeFlow AI executes real tools backed by an official Python Model Context Protocol (MCP) server and persists all state in a SQLite database.

---

## 1. System Architecture

```
                  ┌─────────────────────────────────────┐
                  │    React / Vite Web Dashboard       │
                  │  (Clean, Responsive Tailwind/CSS)   │
                  └──────────────────┬──────────────────┘
                                     │ REST / JSON (/api)
                                     ▼
                  ┌─────────────────────────────────────┐
                  │        FastAPI Web Backend          │
                  │   - Pydantic Input Validation       │
                  │   - Dynamic Health & Audit Traces   │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │   Assistant Orchestration Layer     │
                  │   - Multi-tier Intent Detection     │
                  │   - Ambiguity & Follow-up Handler   │
                  │   - Optional LLM (Gemini / OpenAI)  │
                  │   - Deterministic Fallback Engine   │
                  └──────────────────┬──────────────────┘
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           │                                                   │ In-Process
           │ In-Process                                        │ Tool Call
           ▼                                                   ▼
┌─────────────────────────┐                         ┌─────────────────────────┐
│   Shared Household      │ ◄─── MCP Protocol ────  │   Official Python MCP   │
│     Service Layer       │      (Stdio / SSE)      │         Server          │
│ - Tasks CRUD            │                         │   (mcp.server.mcpserver)│
│ - Reminders CRUD        │                         │   - 10 Exposed Tools    │
│ - Daily Summary Calc    │                         │   - Standalone CLI      │
│ - Simulated Sensor Feed │                         └─────────────────────────┘
└──────────┬──────────────┘
           │ Parameterized SQL
           ▼
┌─────────────────────────┐
│     SQLite Database     │
│   (homeflow.db, ACID)   │
└─────────────────────────┘
```

### Architectural Key Points:
- **Zero Mock Actions**: Natural language commands trigger real operations against the database.
- **Shared Domain Layer**: The REST API and the MCP Server reuse the exact same service functions and data validation schemas.
- **Protocol Transparency**: Browser-to-backend communication uses standard REST. The MCP Server runs over standard MCP transports (stdio/SSE) for external clients like Claude Desktop, Antigravity, or Cursor.
- **Offline Capable & Configurable**: Operates with 100% functionality offline using a deterministic rule-based engine, and automatically upgrades to an LLM if API credentials (`GEMINI_API_KEY` or `OPENAI_API_KEY`) are present in `.env`.

---

## 2. Project Directory Structure

```
homeflow-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI application & lifecycle startup
│   │   ├── database.py                 # SQLite connection & table seeding
│   │   ├── schemas.py                  # Pydantic validation schemas
│   │   ├── mcp_server.py               # Official Python MCP server (10 tools)
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py               # REST API endpoints (/api/*)
│   │   ├── assistant/
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py         # NL parsing, intent routing, trace logger
│   │   │   └── llm_provider.py         # Gemini/OpenAI caller with fallback
│   │   └── services/
│   │       ├── __init__.py
│   │       └── household_service.py    # Core business logic for tasks & reminders
│   ├── tests/
│   │   ├── conftest.py                 # Isolated test database fixture
│   │   ├── test_tasks.py               # Task CRUD & validation tests
│   │   ├── test_reminders.py           # Reminder schedule & overdue tests
│   │   ├── test_summary_and_events.py  # Summary calculations & sensor tests
│   │   ├── test_mcp_tools.py           # MCP tool registry lifecycle tests
│   │   ├── test_assistant.py           # NL parsing & ambiguity tests
│   │   └── test_api.py                 # FastAPI REST endpoint tests
│   ├── requirements.txt                # Backend dependencies
│   └── .env.example                    # Environment variable template
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx              # Branding, date, status pills & summary
│   │   │   ├── DashboardSummary.jsx    # Metric cards (pending, done, reminders)
│   │   │   ├── AssistantChat.jsx       # NL input, quick chips & execution trace
│   │   │   ├── TaskList.jsx            # Task CRUD, filters, priority badges
│   │   │   ├── ReminderList.jsx        # Reminder list, time formatting & modal
│   │   │   ├── EntryEventsTimeline.jsx # Simulated sensor feed & event emitter
│   │   │   ├── DailySummaryModal.jsx   # Factual report modal & clipboard copy
│   │   │   └── McpStatusModal.jsx      # Registered MCP tools & client config
│   │   ├── services/
│   │   │   └── api.js                  # Fetch API wrapper
│   │   ├── App.jsx                     # Top-level state & orchestration
│   │   ├── main.jsx                    # React 18 DOM mount
│   │   └── index.css                   # Custom responsive design system
│   ├── package.json
│   ├── vite.config.js                  # Vite server & proxy configuration
│   └── index.html
├── README.md                           # Documentation & 5-minute demo script
└── .gitignore
```

---

## 3. Installation & Setup Instructions (Windows)

Assume Python 3.11+ and Node.js 18+ are installed.

### Step 1: Open Command Prompt or PowerShell
Navigate to the project root directory:
```powershell
cd C:\Users\sharl\.gemini\antigravity\scratch\homeflow-ai
```

### Step 2: Set up the Python Backend Virtual Environment
```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate
```
*Why this is needed: A virtual environment isolates project dependencies from other Python software on your system.*

### Step 3: Install Backend Dependencies
```cmd
pip install -r requirements.txt
```
*Dependencies installed:*
- `fastapi` & `uvicorn`: Web server & asynchronous REST API.
- `pydantic`: Schema validation.
- `mcp`: Official Model Context Protocol SDK.
- `httpx`: Asynchronous HTTP client for optional LLM calls.
- `pytest`: Automated test framework.
- `python-dotenv`: Environment configuration.

### Step 4: Configure Environment Variables (Optional)
Copy `.env.example` to `.env`:
```cmd
copy .env.example .env
```
*Optional*: If you want to use external LLMs, add your `GEMINI_API_KEY` or `OPENAI_API_KEY`. If left blank, HomeFlow AI operates using its deterministic local rule-based intent engine with zero external network dependencies!

### Step 5: Install Frontend Dependencies
Open a second terminal window and run:
```cmd
cd C:\Users\sharl\.gemini\antigravity\scratch\homeflow-ai\frontend
npm.cmd install
```
*Why `npm.cmd`: In Windows PowerShell, execution policies may block `.ps1` scripts; using `npm.cmd` avoids this restriction.*

---

## 4. Running the Application

### Terminal 1: Start the FastAPI Backend
```cmd
cd C:\Users\sharl\.gemini\antigravity\scratch\homeflow-ai\backend
.venv\Scripts\activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```
- **Backend API URL**: `http://127.0.0.1:8001`
- **Interactive Swagger Docs**: `http://127.0.0.1:8001/docs`
- **Health Check Endpoint**: `http://127.0.0.1:8001/api/health`

### Terminal 2: Start the React / Vite Frontend
```cmd
cd C:\Users\sharl\.gemini\antigravity\scratch\homeflow-ai\frontend
npm.cmd run dev
```
- **Web Dashboard URL**: `http://127.0.0.1:5173`

---

## 5. Running the MCP Server Separately

The official Python MCP server can be launched directly to connect external MCP clients (such as Claude Desktop, Cursor, or the Antigravity agent):

```cmd
cd C:\Users\sharl\.gemini\antigravity\scratch\homeflow-ai\backend
.venv\Scripts\activate
python -m app.mcp_server
```

### Connecting to Claude Desktop / Cursor:
Add this configuration snippet to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "homeflow": {
      "command": "python",
      "args": ["-m", "app.mcp_server"],
      "cwd": "C:\\Users\\sharl\\.gemini\\antigravity\\scratch\\homeflow-ai\\backend"
    }
  }
}
```

### The 10 Registered MCP Tools:
1. `create_task(title, description, category, priority, due_date)`
2. `list_tasks(status, category)`
3. `update_task(task_id, title, description, category, priority, due_date)`
4. `complete_task(task_id)`
5. `delete_task(task_id)`
6. `create_reminder(title, remind_at)`
7. `list_reminders(include_completed)`
8. `complete_reminder(reminder_id)`
9. `get_daily_summary()`
10. `list_simulated_entry_events(limit)`

---

## 6. Running Automated Tests

HomeFlow AI includes 34 unit and integration tests covering CRUD operations, validation errors, daily summary calculations, MCP tool lifecycles, and natural language intent parsing.

To run the complete test suite:
```cmd
cd C:\Users\sharl\.gemini\antigravity\scratch\homeflow-ai\backend
.venv\Scripts\activate
python -m pytest -v
```

All tests execute against an isolated temporary SQLite database, leaving demonstration records intact.

---

## 7. Five-Minute Hackathon Demonstration Script

### Introduction (0:00 - 0:45)
- Open `http://localhost:5173`.
- Present HomeFlow AI: "Modern households struggle with chores, reminders, and entry events scattered across disconnected apps. HomeFlow AI provides a single unified assistant backed by real MCP tool execution."
- Point out the status indicators: Backend API (Connected), MCP Tools (10 registered), and AI Provider (Local Rule Engine or LLM).

### Demo Step 1: Natural Language Task Creation (0:45 - 1:30)
- In the Assistant input area, click the sample prompt chip:
  `"Add a task to clean the kitchen tomorrow."`
- Click **Send**.
- Show the result:
  1. The assistant confirms: *"I've added the task 'Clean the kitchen' (#4) due on [Tomorrow] with medium priority."*
  2. The Task List on the dashboard immediately updates with the new task.
  3. Expand the **Tool Trace** box to show the judge: Tool `create_task` was selected with validated parameters `{"title": "Clean the kitchen", "due_date": "...", "category": "kitchen"}`.

### Demo Step 2: Scheduling a Reminder (1:30 - 2:15)
- Click the prompt chip:
  `"Remind me to call my grandmother at 6 PM."`
- Click **Send**.
- Show the result: The reminder appears in the **Household Reminders** card with its scheduled time and countdown.
- Point out the transparency note: HomeFlow AI clearly discloses this is an in-app reminder rather than fabricating SMS/push notifications.

### Demo Step 3: Completing a Task via NL (2:15 - 3:00)
- Click the prompt chip:
  `"Mark the kitchen cleaning task as completed."`
- Click **Send**.
- Show the result: The assistant matches the task keyword, executes tool `complete_task`, and the dashboard updates with a green checkmark and struck-through title.

### Demo Step 4: Daily Household Summary (3:00 - 3:45)
- Click the prompt chip:
  `"Give me a summary of today's household activities."` (or click the **Daily Summary** button in the header).
- Show the summary modal:
  1. Accurate metrics (Pending chores, Completed tasks, Upcoming reminders, Recent events).
  2. Factual narrative strictly derived from live SQLite records without hallucinating data.
  3. Click **Copy Summary** to show clipboard export.

### Demo Step 5: Simulated Home-Entry Events (3:45 - 4:15)
- Navigate to the **Simulated Entry Events** timeline.
- Point out the `SIMULATED` badges on all sensor entries.
- Use the **Simulate a Live Entry Event** box: select *"Door Opened"* at *"Back Patio"* and click **Emit Event**.
- Show how the event is instantly inserted into the database and appears in the timeline.
- Emphasize safety: This prototype does not control physical door locks or safety-critical alarms.

### Demo Step 6: MCP Transparency & Wrap-Up (4:15 - 5:00)
- Click the **MCP Tools: 10** badge in the header.
- Show the modal displaying the 10 registered tools, input signatures, and the exact configuration to plug this server into external MCP clients.
- Conclude: "HomeFlow AI demonstrates real agentic tool execution, clean architectural separation, and reliable household coordination."

---

## 8. Common Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| `Port 8000/8001 in use (WinError 10048)` | Another application is bound to that port. | Start the server with a custom port: `python -m uvicorn app.main:app --port 8002` and set `PORT=8002`. |
| `npm : File ... npm.ps1 cannot be loaded` | Windows PowerShell script execution policy. | Use `npm.cmd` instead of `npm` (e.g. `npm.cmd run dev`). |
| `TypeError: Failed to fetch` in browser | Backend is not running or port mismatch. | Verify backend is running on `http://127.0.0.1:8001` and `Vite` proxy is set to port 8001. |
| `No module named 'mcp'` | MCP SDK not installed in active environment. | Activate the `.venv` and run `pip install -r requirements.txt`. |

---

## 9. Current Limitations & Roadmap

### Implemented Features
- Real SQLite persistence with seed data deduplication.
- 10 operational tools exposed via the official Python MCP SDK.
- Full CRUD for household tasks with category filtering, priority indicators, and due dates.
- Reminder management with overdue calculation and in-app scheduling.
- Segregated simulated entry events table with live event emitter.
- Daily summary derived from database queries.
- Expandable assistant activity traces with tool names, parameters, and results.
- 34 automated unit and integration tests (100% passing).

### Prototype Limitations
- Notifications are displayed in-app; external SMS/Push services are not hooked up to avoid unverified claims.
- Simulated entry events are synthetic test fixtures and not linked to physical smart locks or security hardware.
- Multi-user authentication is omitted in this prototype to keep demo onboarding instant.

### Next Three High-Priority Improvements
1. **Multi-User Profiles**: Role-based household assignments (e.g. assigning chores to specific family members).
2. **Alexa Skill Adapter**: An Alexa skill bridge translating voice utterances directly into MCP tool calls.
3. **Recurring Task Rules**: Automated CRON recurrence for chores (e.g., "Replace HVAC filter every 90 days").

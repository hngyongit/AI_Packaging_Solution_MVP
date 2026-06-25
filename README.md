# AI Packaging Solution Chat Bot

An **AI packaging consultant chatbot** built with **Python (FastAPI) + MongoDB** on the backend and **Vite + React + Tailwind CSS** on the frontend. The agent uses an LLM to **think → call tools → observe results → respond**, making it capable of retrieving real-time data (contracts, inventory, etc.) instead of just generating text.

The frontend features a **professional industrial design** with a brand-green packaging theme, optimized for B2B carton sales with clean layouts and trust-focused messaging.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [1. Backend Setup](#1-backend-setup)
  - [2. Frontend Setup](#2-frontend-setup)
  - [3. LLM Configuration](#3-llm-configuration)
- [How the Agent Works](#how-the-agent-works)
- [Tool System](#tool-system)
  - [BaseTool Interface](#basetool-interface)
  - [Registry](#registry)
  - [How to Add a New Tool](#how-to-add-a-new-tool)
- [API Reference](#api-reference)
- [Frontend Guide](#frontend-guide)
- [Deployment](#deployment)
- [Contributing Guide](#contributing-guide)
- [Environment Variables](#environment-variables)

---

## Architecture Overview

```
┌─────────────┐      ┌──────────────────┐      ┌──────────────┐
│  Frontend   │─────▶│  Backend (API)   │─────▶│    MongoDB    │
│  Vite+React │      │  FastAPI + Agent │      │  localhost    │
│  :5173      │◀─────│  :8000           │◀─────│  :27017       │
└─────────────┘      └───────┬──────────┘      └──────────────┘
                             │
                    ┌────────▼────────┐
                    │   LLM (OpenAI   │
                    │   compatible)   │
                    │  e.g. Ollama,   │
                    │  9router, etc.  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Tool System   │
                    │  (tools/*.py)   │
                    │                 │
                    │ search_contract │
                    │ search_inventory│
                    │   (extensible)  │
                    └─────────────────┘
```

**Flow:**
1. User sends a message → Frontend calls `POST /api/chat`
2. Backend saves the user message to MongoDB
3. **Agent** (`app/services/agent.py`) starts:
   - **Think** — Prepares a system prompt listing all available tools with descriptions & JSON schemas
   - **Act** — Calls the LLM → LLM may output `<tool_call>` with JSON specifying which tool to invoke
   - **Observe** — Parses the tool call, runs the actual tool, injects the result back into context
   - **Respond** — Calls the LLM again with the tool result → LLM produces a final answer
4. Backend saves the assistant response to MongoDB
5. Frontend receives both the user message and bot reply (plus tool-call logs)

---

## Project Structure

```
AIPackagingSolutionChatBot/
│
├── backend/                          # Python FastAPI server
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI entry point, CORS, router registration
│   │   ├── config.py                 # Reads .env → Settings class
│   │   ├── database.py               # MongoDB connection (pymongo)
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py            # Pydantic models: MessageCreate, MessageResponse, etc.
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── chat.py               # API endpoints: conversations CRUD + chat
│   │   ├── agent_config.py           # ★ Configurable parameters (memory, history)
│   │   ├── system_prompt.md          # ★ LLM personality & instructions (Markdown)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── agent.py              # ★ The agent brain (think → act → observe → respond)
│   │
│   ├── tools/                        # ★ AI-callable tools (extensible)
│   │   ├── __init__.py               #   Re-exports for easy import
│   │   ├── base.py                   #   BaseTool abstract class (ABC)
│   │   ├── registry.py               #   Tool registry (register / get / list)
│   │   ├── search_contract.py        #   Template — search contracts by keyword (NOT YET IMPLEMENTED)
│   │   ├── search_inventory.py       #   Template — search inventory items (NOT YET IMPLEMENTED)
│   │   └── llm_config.py             #   Deprecated (not used — kept as reference)
│   │
│   ├── .env                          # Backend environment variables
│   ├── requirements.txt              # Python dependencies
│   ├── run.py                        # uvicorn launcher
│   └── venv/                         # Virtual environment (git-ignored)
│
├── frontend/                         # Vite + React + Tailwind CSS
│   ├── public/
│   │   └── vite.svg
│   ├── src/
│   │   ├── main.jsx                  # React entry point
│   │   ├── index.css                 # Tailwind directives + animations & light scrollbar
│   │   ├── App.jsx                   # ★ Main app: state, send message, tool-call rendering, title dedup
│   │   ├── api.js                    #   Axios API client (all backend calls)
│   │   └── components/
│   │       ├── ChatMessage.jsx       #   Message bubble (user / AI / tool / error)
│   │       ├── Sidebar.jsx           #   Conversation list panel with branding
│   │       └── EmptyState.jsx        #   Welcome screen when no conversation is active
│   ├── .env                          # Frontend environment variables
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js                # Dev proxy /api → localhost:8000
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── README.md                         # ← You are here
└── .gitignore
```

---

## Quick Start

### Prerequisites

| Tool      | Version   | Notes                                       |
|-----------|-----------|---------------------------------------------|
| Python    | ≥ 3.10    | Tested with 3.13                            |
| Node.js   | ≥ 18      |                                             |
| MongoDB   | ≥ 6       | Running on `localhost:27017` (configurable in `.env`) |
| LLM       | Any       | OpenAI-compatible API (Ollama, 9router, etc.) |

### 1. Backend Setup

```bash
# Clone & enter backend
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
.\venv\Scripts\activate
# Linux / macOS:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python run.py
```

The API is now running at **http://localhost:8000**.  
Swagger docs are available at **http://localhost:8000/docs**.

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The UI opens at **http://localhost:5173**.

> **Note:** The Vite dev server proxies `/api/*` requests to `localhost:8000`, so the frontend can talk to the backend without CORS issues in development.

### 3. LLM Configuration

Edit `backend/.env`:

```env
# Your LLM endpoint (OpenAI-compatible chat completions)
LLM_API_URL=http://localhost:11434/v1/chat/completions
LLM_MODEL=llama3
```

> **Note:** The code default in `config.py` is `http://localhost:11434/api/generate`, but the agent expects an OpenAI-compatible `/v1/chat/completions` endpoint. Set `LLM_API_URL` in `.env` to the correct URL for your provider.

**With Ollama (recommended for local dev):**
```bash
# Install Ollama from https://ollama.com
ollama pull llama3          # or any model you like
```

**With a custom API (e.g. 9router, OpenAI proxy):**  
Just point `LLM_API_URL` to the `/v1/chat/completions` endpoint of your API.

> The agent expects an OpenAI-compatible format: `data["choices"][0]["message"]["content"]`.

---

## How the Agent Works

The agent lives in **`backend/app/services/agent.py`** and follows a **ReAct** (Reasoning + Acting) loop:

```
                    ┌─────────────────────────────┐
                    │  User sends a message       │
                    └─────────────┬───────────────┘
                                  ▼
                    ┌─────────────────────────────┐
                    │  Agent builds system prompt  │
                    │  + conversation history      │
                    │  + list of available tools   │
                    └─────────────┬───────────────┘
                                  ▼
                    ┌─────────────────────────────┐
          ┌────────▶│  Call LLM                   │
          │         └─────────────┬───────────────┘
          │                       ▼
          │         ┌─────────────────────────────┐
          │         │  Parse response             │
          │         │  Does it contain            │
          │         │  <tool_call>...</tool_call>? │
          │         └─────────────┬───────────────┘
          │                       ▼
          │              ┌─── YES ────┐  NO ────┐
          │              ▼                     ▼
          │  ┌──────────────────────┐  ┌──────────────┐
          │  │ Extract tool name    │  │ Return final │
          │  │ & arguments from JSON│  │ answer       │
          │  │                      │  │ to frontend  │
          │  │ Run the tool         │  └──────────────┘
          │  │ (real implementation)│
          │  │                      │
          │  │ Inject result back   │
          │  │ into LLM context     │
          │  └──────────┬───────────┘
          │             │
          └─────────────┘
          (max 5 iterations by default — configurable via `AGENT_MAX_TOOL_ITERATIONS`)
```

**Example agent conversation (internal):**

```
System: You are an AI assistant. Available tools:
  - search_contract: Search contracts by keyword. Params: {"query": "..."}
  - search_inventory: Search inventory items. Params: {"item_name": "..."}

User: Do we have any active maintenance contracts?

Assistant:
  <tool_call>
  {"name": "search_contract", "arguments": {"query": "maintenance"}}
  </tool_call>

[Agent detects tool call → runs search_contract("maintenance") → injects result]

User: Tool 'search_contract' was called with arguments {"query": "maintenance"}.
Result:
  - Contract #C-1002: Maintenance Contract ($12,000)

Now provide your final answer to the user based on this data.

Assistant: Yes, we have one active maintenance contract:
**Contract #C-1002** — Maintenance Contract valued at **$12,000**.
```

---

## Agent Configuration

All chatbot behaviour parameters are centralized in **`backend/app/agent_config.py`** — no need to dig through multiple files to change how the agent works.

| Setting                    | Env variable                  | Default | Description                                         |
|----------------------------|-------------------------------|---------|-----------------------------------------------------|
| `MAX_HISTORY`              | `AGENT_MAX_HISTORY`           | `50`    | Number of recent messages to feed as LLM context    |
| `MAX_TOOL_ITERATIONS`      | `AGENT_MAX_TOOL_ITERATIONS`   | `5`     | Max tool-call loops before forcing a final answer   |
| `SYSTEM_PROMPT`            | `AGENT_SYSTEM_PROMPT`         | *(see below)* | Base personality + instructions for the LLM    |

### How to customise

**Quick override via `.env`:**

```env
AGENT_MAX_HISTORY=20
AGENT_MAX_TOOL_ITERATIONS=3
```

**System prompt — edit the `.md` file:**

The agent's personality and instructions live in **`backend/app/system_prompt.md`**.  
Edit this file directly — it's plain Markdown, no code to touch.  
The `{tool_descriptions}` placeholder is automatically replaced with the registered tools list.

```bash
# Just edit the markdown file and restart the backend
notepad backend/app/system_prompt.md
```

**Override via `.env` (advanced):**

For environments where you can't edit files (e.g. Docker), set `AGENT_SYSTEM_PROMPT` in your `.env`.

### What `MAX_HISTORY` affects

- `MAX_HISTORY=50` → agent sees the last 50 user+assistant messages. Good for long conversations.
- `MAX_HISTORY=10` → cheaper/faster, but the agent may forget earlier context.
- Also controls how many messages are fetched from MongoDB in `chat.py`.

---

## Tool System

Tools are the only way the AI can interact with real data. Each tool is a Python class that the agent discovers automatically.

### BaseTool Interface

File: `backend/tools/base.py`

```python
from abc import ABC, abstractmethod

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...
    @property
    @abstractmethod
    def description(self) -> str: ...
    @property
    @abstractmethod
    def parameters(self) -> dict: ...     # JSON Schema
    @abstractmethod
    async def run(self, **kwargs) -> str: ...
```

| Property      | What it's used for                                    |
|---------------|-------------------------------------------------------|
| `name`        | How the LLM refers to the tool in `<tool_call>` JSON  |
| `description` | Natural-language description → helps the LLM decide   |
| `parameters`  | JSON Schema describing expected arguments             |
| `run()`       | Actual logic — return a **string** for the LLM to read |

### Registry

File: `backend/tools/registry.py`

- **`register(tool)`** — add a tool to the registry
- **`get_tool(name)`** — look up by name
- **`list_tools()`** — get all tools
- **`tool_descriptions()`** — formatted for the system prompt

Tools are **not registered automatically** — you must explicitly call `register()` in your own code (typically at import time or in an app startup hook).

### How to Add a New Tool

> **⚠️ Known issue:** The template tools `search_contract` and `search_inventory` are defined but **not yet registered** — you must call `register()` on them before the agent can discover them. See [Quick fix](#registering-existing-tools) below.

1. **Create a file** `backend/tools/your_tool.py`

```python
from tools.base import BaseTool

class SearchCustomer(BaseTool):
    @property
    def name(self) -> str:
        return "search_customer"

    @property
    def description(self) -> str:
        return "Look up customer details by name or ID."

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Customer name or ID"},
            },
            "required": ["query"],
        }

    async def run(self, query: str) -> str:
        # ── Your real implementation here ────────────────────
        # Query a database, call an external API, etc.
        return f"Customer: {query}, Status: Active, Balance: $0"
```

2. **Register it** wherever makes sense for your app (e.g. in `backend/tools/registry.py` or in an app startup event):

```python
from tools.registry import register
from tools.your_tool import SearchCustomer

register(SearchCustomer())
```

That's it! The agent will automatically include `search_customer` in its system prompt on the next request.

> **Important:** The `run()` method must return a **plain string**. The LLM reads this string to formulate its answer. Format it clearly — use newlines, bullet points, etc.

#### Registering existing tools

The template tools (`SearchContract`, `SearchInventory`) are defined but **never registered**. To enable them, add this code in `backend/app/main.py` (or wherever you initialize the app):

```python
from tools.registry import register
from tools.search_contract import SearchContract
from tools.search_inventory import SearchInventory

# Register built-in tools
register(SearchContract())
register(SearchInventory())
```

> ℹ️ Without calling `register()`, the agent will **not** know about these tools, and they will not appear in the system prompt.

---

## API Reference

| Method | Endpoint                              | Description                           | Auth |
|--------|---------------------------------------|---------------------------------------|------|
| GET    | `/api/health`                         | Health check                          | —    |
| GET    | `/api/conversations`                  | List conversations (latest 50)        | —    |
| POST   | `/api/conversations?title=...`        | Create a new conversation             | —    |
| DELETE | `/api/conversations/{id}`             | Delete a conversation + its messages  | —    |
| GET    | `/api/conversations/{id}/messages`    | Get all messages in a conversation    | —    |
| POST   | `/api/chat`                           | Send message → agent processes → respond | — |

### `POST /api/chat`

**Request:**
```json
{
  "conversation_id": "optional-conversation-id",
  "content": "What contracts do we have?"
}
```

**Response:**
```json
{
  "user_message": {
    "id": "...",
    "conversation_id": "...",
    "role": "user",
    "content": "What contracts do we have?",
    "timestamp": "2026-06-22T..."
  },
  "bot_message": {
    "id": "...",
    "conversation_id": "...",
    "role": "assistant",
    "content": "We have 3 contracts...",
    "timestamp": "2026-06-22T..."
  },
  "conversation_id": "...",
  "tool_calls": [
    {
      "name": "search_contract",
      "arguments": {"query": "contracts"},
      "result": "..."
    }
  ]
}
```

If no `conversation_id` is provided, a new conversation is auto-created.

---

## Frontend Guide

### Key files

| File | Purpose |
|------|---------|
| `src/App.jsx` | Main state management, `handleSend` with optimistic updates, rendering tool-call logs, deduplication of first message when used as title |
| `src/api.js` | Axios client — all backend calls in one place |
| `src/components/ChatMessage.jsx` | Renders 4 message types: **user** (right-aligned, emerald gradient), **AI** (left, white card with sharp shadow), **tool** (amber, monospace), **error** (red) |
| `src/components/Sidebar.jsx` | Conversation list with create/delete, branded "AI Packaging" header |
| `src/components/EmptyState.jsx` | Welcome screen with "AI Packaging Solution" branding |

### How tool calls appear in the UI

When the agent calls one or more tools, the frontend renders amber-colored tool-call bubbles between the user's message and the AI's response. Each bubble shows:
- 🔧 Tool name
- Arguments passed
- Raw result returned

### UI Theme

The frontend uses a **light-mode, space-sharp design**:
- **Color palette:** Clean white/slate base with **emerald green** primary accent (packaging/sustainability theme), violet secondary
- **Typography:** Sharp `rounded-xl` containers with asymmetric `rounded-br-sm`/`rounded-bl-sm` corners
- **Shadows:** Crisp `shadow-sharp` (2-layer box-shadow) instead of blurry shadows
- **Playful touches:** Gradient avatars, `animate-bounce` typing indicator, gradient buttons with hover transitions

### Title deduplication

When a new conversation is created, the first user message is used as the conversation title. The frontend automatically detects this and **hides** the first user message from the chat view to avoid duplication — the title appears only in the sidebar and the chat header.

```js
// App.jsx — filteredMessages logic
const filteredMessages = (() => {
    if (!activeConv || !messages.length) return messages
    const title = activeConv.title
    if (!title || title === 'New Chat' || title === 'Untitled') return messages
    const firstMsg = messages[0]
    if (firstMsg.role === 'user' && firstMsg.content && firstMsg.content.startsWith(title)) {
        return messages.slice(1)
    }
    return messages
})()
```

### Vite Proxy

The `vite.config.js` proxies `/api/*` to the backend. In development, the frontend `.env` has `VITE_API_URL=` (empty) so all requests stay on the same origin.

---

## Deployment

### Production backend

```bash
cd backend
# Install dependencies (no hot-reload)
pip install -r requirements.txt
# Run with uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Production frontend

```bash
cd frontend
npm run build     # outputs to dist/
# Serve dist/ with nginx, a static file server, or your backend
```

### nginx example (serving both)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /path/to/frontend/dist;
        try_files $uri /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### MongoDB

For production, use MongoDB Atlas or a properly configured self-hosted instance. Update `MONGODB_URI` in `backend/.env`.

---

## Contributing Guide

### Code style

- **Python:** Follow PEP 8. Use type hints.
- **JavaScript:** Follow standard React conventions (functional components, hooks).
- **Tools:** Every tool must extend `BaseTool` and be registered in `registry.py`.
- **Missing `.gitignore`:** The project currently lacks a `.gitignore` — consider adding one to exclude `node_modules/`, `venv/`, `.venv/`, `__pycache__/`, `.env`, and `dist/`.

### Adding a tool workflow

1. Create `backend/tools/my_tool.py` with a class extending `BaseTool`
2. Implement `name`, `description`, `parameters`, and `run()`
3. Register in `backend/tools/registry.py`
4. Done — no other changes needed

### Running tests

```bash
cd backend
python -m pytest                    # if tests exist
cd ../frontend
npm test                            # if tests exist
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable                    | Default                                     | Description                                      |
|-----------------------------|---------------------------------------------|--------------------------------------------------|
| `MONGODB_URI`               | `mongodb://localhost:27017/chatbot_db`       | MongoDB connection string                        |
| `LLM_API_URL`               | `http://localhost:11434/api/generate`        | OpenAI-compatible LLM endpoint (override in `.env`) |
| `LLM_MODEL`                 | `llama3`                                    | Model name to use                                |
| `SECRET_KEY`                | `default-secret`                             | For future auth features                         |
| `AGENT_MAX_HISTORY`         | `50`                                        | Recent messages to include as LLM context        |
| `AGENT_MAX_TOOL_ITERATIONS` | `5`                                         | Max tool-call loops before forcing final answer  |
| `AGENT_SYSTEM_PROMPT`       | *(loaded from `app/system_prompt.md`)*       | Full system prompt override (advanced)           |

### Frontend (`frontend/.env`)

| Variable       | Default | Description                                              |
|----------------|---------|----------------------------------------------------------|
| `VITE_API_URL` | (empty) | Backend URL. Leave empty to use Vite proxy in dev mode.  |

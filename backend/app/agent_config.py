"""
Agent configuration — tune chatbot behaviour without touching code.

All values can be overridden via environment variables in backend/.env.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── Load system prompt from markdown file ──────────────────────
# Edit app/system_prompt.md to change the LLM's personality/instructions.
# The {tool_descriptions} placeholder is auto-replaced with the
# registered tools list. To override via .env, set AGENT_SYSTEM_PROMPT.
_PROMPT_FILE = Path(__file__).resolve().parent / "system_prompt.md"

if _PROMPT_FILE.exists():
    with open(_PROMPT_FILE, encoding="utf-8") as f:
        _DEFAULT_PROMPT = f.read().strip()
else:
    _DEFAULT_PROMPT = "You are a helpful AI assistant.\n\n{tool_descriptions}"


class AgentConfig:
    # ── Conversation memory ────────────────────────────────────
    # How many recent messages (user + assistant) to include as
    # context when calling the LLM. Higher = more memory but more
    # tokens (and slower responses).
    MAX_HISTORY: int = int(os.getenv("AGENT_MAX_HISTORY", "50"))

    # ── Tool-calling loop ──────────────────────────────────────
    # Maximum number of tool-call iterations before the agent is
    # forced to return an answer. Prevents infinite loops.
    MAX_TOOL_ITERATIONS: int = int(os.getenv("AGENT_MAX_TOOL_ITERATIONS", "5"))

    # ── System prompt ──────────────────────────────────────────
    # Loaded from system_prompt.md by default.
    # Override via AGENT_SYSTEM_PROMPT in .env if needed.
    SYSTEM_PROMPT: str = os.getenv("AGENT_SYSTEM_PROMPT", _DEFAULT_PROMPT)


agent_config = AgentConfig()
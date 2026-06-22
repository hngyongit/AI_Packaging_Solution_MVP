"""
Agent service — the brain that orchestrates:

  1. Think — LLM receives tools list + user query, decides which tool(s) to call.
  2. Act  — invoke the tool, get structured result.
  3. Observe — inject tool output into the LLM context and ask it to respond.
  4. Respond — return final answer with a record of what was called.
"""

import json
import re
from typing import Any

import httpx
from app.config import settings
from app.agent_config import agent_config
from tools import get_tool, tool_descriptions


# ── Parsing helpers ────────────────────────────────────────────

_TOOL_CALL_RE = re.compile(
    r"<tool_call>\s*({.*?})\s*</tool_call>", re.DOTALL
)


def _parse_tool_call(text: str) -> dict | None:
    """Extract the first <tool_call> JSON block from LLM output."""
    match = _TOOL_CALL_RE.search(text)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def _build_agent_messages(
    user_prompt: str,
    context: list[dict],
) -> list[dict]:
    """Build the full messages list for the agent loop."""
    system_content = agent_config.SYSTEM_PROMPT.format(
        tool_descriptions=tool_descriptions()
    )
    messages: list[dict] = [
        {"role": "system", "content": system_content},
    ]

    # Inject conversation history (trim to MAX_HISTORY most recent)
    if context:
        recent = context[-agent_config.MAX_HISTORY:]
        history_lines = []
        for msg in recent:
            label = "chatBot" if msg["role"] == "assistant" else "user"
            history_lines.append(f"{label}:\n{msg['content']}")
        messages.append({
            "role": "user",
            "content": f"Previous conversation:\n\n" + "\n\n".join(history_lines),
        })

    # Current user prompt
    messages.append({"role": "user", "content": user_prompt})
    return messages


async def _llm_call(messages: list[dict]) -> str:
    """Send messages to the LLM and return the content text."""
    payload = {
        "model": settings.LLM_MODEL,
        "messages": messages,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(settings.LLM_API_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()
    return data["choices"][0]["message"]["content"]


# ── Main agent loop ────────────────────────────────────────────

async def agent_run(user_prompt: str, context: list[dict]) -> dict:
    """Run the agent: think → call tool (if needed) → respond.

    Returns:
        {"content": "...", "tool_calls": [...]}
    """
    messages = _build_agent_messages(user_prompt, context)
    tool_calls_log: list[dict] = []

    # ── Loop — let the LLM decide to call tools ────────────────
    max_iter = agent_config.MAX_TOOL_ITERATIONS
    for _ in range(max_iter):
        response_text = await _llm_call(messages)
        tool_call = _parse_tool_call(response_text)

        if tool_call is None:
            # No tool call → agent is done → return final answer
            return {
                "content": response_text,
                "tool_calls": tool_calls_log,
            }

        # ── Execute tool ────────────────────────────────────────
        name = tool_call.get("name", "unknown")
        args = tool_call.get("arguments", {})
        tool = get_tool(name)

        if tool is None:
            result = f"Error: tool '{name}' not found."
        else:
            try:
                result = await tool.run(**args)
            except Exception as e:
                result = f"Error executing '{name}': {e}"

        tool_calls_log.append({
            "name": name,
            "arguments": args,
            "result": result,
        })

        # Feed observation back to the LLM
        messages.append({
            "role": "user",
            "content": (
                f"Tool '{name} was called with arguments {json.dumps(args)}.\n"
                f"Result:\n{result}\n\n"
                f"Now provide your final answer to the user based on this data."
            ),
        })

    # Fallback — loop exhausted without a final answer
    return {
        "content": "I couldn't finish processing your request. Please try again.",
        "tool_calls": tool_calls_log,
    }

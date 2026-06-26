"""
Agent service — the brain that orchestrates:

  1. Think — LLM receives tools list + user query, decides which tool(s) to call.
  2. Act  — invoke the tool, get structured result.
  3. Observe — inject tool output into the LLM context and ask it to respond.
  4. Respond — return final answer with a record of what was called.
"""


import json
from typing import Any

import httpx
from app.config import settings
from app.agent_config import agent_config
from tools import get_tool, tool_descriptions


def _extract_balanced(text: str, start: int) -> str | None:
    """Extract a balanced {...} JSON object starting at *start*."""
    if start >= len(text) or text[start] != "{":
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _parse_tool_call(text: str) -> dict | None:
    """Extract the first <tool_call> JSON block (brace-depth aware)."""
    try:
        tag_start = text.find("<tool_call>")
        if tag_start == -1:
            return None
        brace_at = text.find("{", tag_start)
        if brace_at == -1:
            return None
        raw = _extract_balanced(text, brace_at)
        if raw is None:
            return None
        after = text[brace_at + len(raw) :]
        if "</tool_call>" not in after[:50]:
            return None
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError, IndexError):
        return None


def _build_agent_messages(
    user_prompt: str,
    context: list[dict],
) -> list[dict]:
    """Build the full messages list for the agent loop."""
    system_content = agent_config.SYSTEM_PROMPT.replace(
        "{tool_descriptions}", tool_descriptions()
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
    headers = {"Content-Type": "application/json"}
    if settings.SECRET_KEY and settings.SECRET_KEY != "default-secret":
        headers["Authorization"] = f"Bearer {settings.SECRET_KEY}"

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(settings.LLM_API_URL, json=payload, headers=headers)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError:
            raise RuntimeError(
                f"LLM API returned HTTP {resp.status_code}: {resp.text[:500]}"
            )
        try:
            data = resp.json()
        except Exception as e:
            raise RuntimeError(
                f"LLM API returned invalid JSON (status {resp.status_code}): "
                f"{resp.text[:300]!r}"
            )
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(
            f"LLM API response missing 'content' field. "
            f"Response keys: {list(data.keys())}. "
            f"Error: {e}. Raw: {str(data)[:300]}"
        )


# ── Main agent loop ────────────────────────────────────────────

async def agent_run(user_prompt: str, context: list[dict]) -> dict:
    """Run the agent: think → call tool (if needed) → respond.

    Returns:
        {"content": "...", "tool_calls": [...], "mockup_task_id": "..."}
    """
    messages = _build_agent_messages(user_prompt, context)
    tool_calls_log: list[dict] = []
    mockup_task_id: str | None = None

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
                "mockup_task_id": mockup_task_id,
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

        # ── Detect mockup generation & extract task_id ─────────
        if name == "generate_mockup":
            try:
                parsed = json.loads(result)
                if parsed.get("status") == "queued":
                    mockup_task_id = parsed.get("task_id")
            except (json.JSONDecodeError, TypeError):
                pass

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
        "mockup_task_id": mockup_task_id,
    }

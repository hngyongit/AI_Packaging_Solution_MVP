import httpx
from app.config import settings
from tools.llm_config import (
    SYSTEM_PROMPT,
    USER_LABEL,
    BOT_LABEL,
    MAX_HISTORY_TURNS,
    USE_SYSTEM_PROMPT,
)


def _format_context(context: list[dict]) -> str:
    """Convert message history into a plain-text conversation block.

    Format:
        user: ...
        chatBot: ...
    """
    lines: list[str] = []
    for msg in context:
        label = BOT_LABEL if msg["role"] == "assistant" else USER_LABEL
        lines.append(f"{label}:\n{msg['content']}")
    return "\n\n".join(lines)


async def query_llm(prompt: str, context: list[dict] | None = None) -> str:
    """Send a prompt to an OpenAI-compatible LLM API and return the response."""
    messages: list[dict] = []

    # Optional system prompt
    if USE_SYSTEM_PROMPT:
        messages.append({"role": "system", "content": SYSTEM_PROMPT})

    # Build conversation history — trim oldest messages to MAX_HISTORY_TURNS
    if context:
        trimmed = context[-(MAX_HISTORY_TURNS * 2):]
        history_block = _format_context(trimmed)
        if history_block:
            messages.append({
                "role": "user",
                "content": f"Here is the conversation so far:\n\n{history_block}",
            })

    # Current user message in the same format
    messages.append({
        "role": "user",
        "content": f"{USER_LABEL}:\n{prompt}",
    })

    payload = {
        "model": settings.LLM_MODEL,
        "messages": messages,
        "stream": False,
    }

    headers = {"Content-Type": "application/json"}
    if settings.SECRET_KEY and settings.SECRET_KEY != "default-secret":
        headers["Authorization"] = f"Bearer {settings.SECRET_KEY}"

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(settings.LLM_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    # OpenAI-compatible format: data["choices"][0]["message"]["content"]
    return data["choices"][0]["message"]["content"]

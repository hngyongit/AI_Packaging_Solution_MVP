"""
Mockup service — polls Lumicraft API for image generation status,
and provides real-time SSE streaming.

Supports both polling (legacy) and SSE (new) approaches.
"""
import asyncio
import json
import time

import httpx
from app.config import settings

# In-memory cache: task_id -> {status, image_url, message, cached_at}
_cache: dict[str, dict] = {}

_LUMICRAFT_BASE = "https://api.lumicraft.io/v1"

def _extract_image_url(data: dict) -> str | None:
    """Extract image URL from Lumicraft API polling response.

    The `complete` SSE event and the polling response both place
    ``result_url`` at the root level.  Fall back to the legacy nested
    ``result.data[0].url`` path just in case.
    """
    # Primary: root-level result_url (matches SSE complete-event shape)
    url = data.get("result_url")
    if url:
        return url
    # Fallback: nested inside result.data[0].url
    try:
        result_data = data.get("result")
        if result_data and isinstance(result_data, dict):
            items = result_data.get("data", [])
            if isinstance(items, list) and len(items) > 0:
                for item in items:
                    url = item.get("url") or item.get("image_url")
                    if url:
                        return url
    except Exception:
        pass
    return None

async def get_or_poll_status(task_id: str) -> dict:
    """Return cached status if fresh, otherwise poll Lumicraft API."""
    # Check cache — only return cached COMPLETED/FAILED results to avoid re-polling
    cached = _cache.get(task_id)
    if cached and cached["status"] in ("COMPLETED", "FAILED", "ERROR"):
        return cached

    api_key = settings.LUMICRAFT_API_KEY
    if not api_key:
        return {"status": "ERROR", "image_url": None, "message": "API key not configured"}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{_LUMICRAFT_BASE}/images/generations/{task_id}",
                headers={"Authorization": f"Bearer {api_key}"},
            )

        if resp.status_code == 404:
            result = {"status": "ERROR", "image_url": None, "message": "Task not found"}
        elif resp.status_code != 200:
            result = {
                "status": "ERROR",
                "image_url": None,
                "message": f"Status check failed ({resp.status_code})",
            }
        else:
            data = resp.json()
            result = {
                "status": data.get("status", "UNKNOWN"),
                "image_url": _extract_image_url(data),
                "message": data.get("message", ""),
            }

        # Cache completed/failed results; let in-progress tasks re-check
        if result["status"] in ("COMPLETED", "FAILED", "ERROR"):
            result["cached_at"] = time.time()
            _cache[task_id] = result
        return result

    except httpx.TimeoutException:
        return {"status": "UNKNOWN", "image_url": None, "message": "Timed out polling status"}
    except Exception as e:
        return {"status": "ERROR", "image_url": None, "message": str(e)}

async def poll_until_complete(task_id: str) -> dict:
    """Poll Lumicraft until the task completes or times out."""
    start = time.time()
    max_time = settings.MOCKUP_MAX_POLL_TIME
    interval = settings.MOCKUP_POLL_INTERVAL

    while time.time() - start < max_time:
        result = await get_or_poll_status(task_id)
        if result["status"] in ("COMPLETED", "FAILED", "ERROR"):
            return result
        await asyncio.sleep(interval)

    return {"status": "TIMEOUT", "image_url": None, "message": "Image generation timed out"}

# ── Real-time SSE streaming ────────────────────────────────────

async def sse_events(task_id: str):
    """Async generator that yields SSE events from Lumicraft.

    Each yielded value is a dict with keys:
      - event: "status" | "progress" | "complete"
      - data: parsed JSON payload
    """
    api_key = settings.LUMICRAFT_API_KEY
    if not api_key:
        yield {"event": "complete", "data": {"status": "ERROR", "result_url": None, "error": "API key not configured"}}
        return

    url = f"https://api.lumicraft.io/api/events/{task_id}?token={api_key}"

    try:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("GET", url) as response:
                if response.status_code != 200:
                    yield {
                        "event": "complete",
                        "data": {
                            "status": "ERROR",
                            "result_url": None,
                            "error": f"SSE connection failed (HTTP {response.status_code})",
                        },
                    }
                    return

                # Read raw SSE bytes and parse manually
                buffer = b""
                async for chunk in response.aiter_bytes():
                    if not chunk:
                        continue
                    buffer += chunk
                    while b"\n\n" in buffer:
                        raw_msg, buffer = buffer.split(b"\n\n", 1)
                        sse_data = _parse_sse(raw_msg.decode("utf-8", errors="replace"))
                        if sse_data:
                            yield sse_data
                            if sse_data["event"] in ("complete", "error"):
                                d = sse_data["data"]
                                if d.get("result_url"):
                                    _cache[task_id] = {
                                        "status": "COMPLETED",
                                        "image_url": d["result_url"],
                                        "message": "",
                                        "cached_at": time.time(),
                                    }
                                else:
                                    _cache[task_id] = {
                                        "status": d.get("status", "FAILED"),
                                        "image_url": None,
                                        "message": d.get("error", "Unknown error"),
                                        "cached_at": time.time(),
                                    }
                                return
    except httpx.TimeoutException:
        yield {"event": "complete", "data": {"status": "ERROR", "result_url": None, "error": "SSE connection timed out"}}
    except Exception as e:
        yield {"event": "complete", "data": {"status": "ERROR", "result_url": None, "error": str(e)}}

def _parse_sse(text: str) -> dict | None:
    """Parse a single SSE message text into {event, data}."""
    event = "message"
    data_str = ""
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("event:"):
            event = line[len("event:"):].strip()
        elif line.startswith("data:"):
            data_str += line[len("data:"):].strip() + "\n"
    data_str = data_str.strip()
    if not data_str:
        return None
    try:
        parsed = json.loads(data_str)
    except json.JSONDecodeError:
        return {"event": event, "data": {"raw": data_str}}
    return {"event": event, "data": parsed}

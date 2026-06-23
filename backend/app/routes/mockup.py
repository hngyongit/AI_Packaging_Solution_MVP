"""
Route: GET  /api/mockup/status/{task_id}   (polling fallback)
       GET  /api/mockup/sse/{task_id}      (real-time SSE)
       PATCH /api/mockup/message/{message_id}

Allows the frontend to poll or stream mockup generation progress
and persist the final image URL on the bot message.
"""
import json
from bson import ObjectId
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.database import messages_collection
from app.services.mockup_service import get_or_poll_status, sse_events

router = APIRouter()

class UpdateMessageImage(BaseModel):
    image_url: str

@router.get("/mockup/status/{task_id}")
async def mockup_status(task_id: str):
    """Get the current status of a mockup generation task (polling fallback)."""
    try:
        result = await get_or_poll_status(task_id)
        result.pop("cached_at", None)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mockup/sse/{task_id}")
async def mockup_sse(task_id: str):
    """Real-time SSE stream of mockup generation progress."""
    return StreamingResponse(
        _sse_generator(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

async def _sse_generator(task_id: str):
    """Generator that wraps sse_events into SSE wire format."""
    async for event in sse_events(task_id):
        yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"

@router.patch("/mockup/message/{message_id}")
async def update_mockup_image(message_id: str, body: UpdateMessageImage):
    """Persist the generated image URL on the bot message document."""
    update_result = messages_collection.update_one(
        {"_id": ObjectId(message_id)},
        {"$set": {"image_url": body.image_url}},
    )
    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"ok": True}

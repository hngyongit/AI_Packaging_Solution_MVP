from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime, timezone

from app.database import messages_collection, conversations_collection
from app.models.schemas import MessageCreate, MessageResponse, ConversationResponse
from app.services.agent import agent_run
from app.agent_config import agent_config

router = APIRouter()


def _serialize_doc(doc) -> dict:
    """Convert MongoDB document to a JSON-serializable dict."""
    doc["id"] = str(doc.pop("_id"))
    return doc


# ── Conversations ──────────────────────────────────────────────


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations():
    docs = (
        conversations_collection.find()
        .sort("updated_at", -1)
        .limit(50)
    )
    return [_serialize_doc(doc) for doc in docs]


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(title: str = "New Chat"):
    now = datetime.now(timezone.utc)
    result = conversations_collection.insert_one(
        {"title": title, "created_at": now, "updated_at": now}
    )
    doc = conversations_collection.find_one({"_id": result.inserted_id})
    return _serialize_doc(doc)


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    conversations_collection.delete_one({"_id": ObjectId(conversation_id)})
    messages_collection.delete_many({"conversation_id": conversation_id})
    return {"message": "Conversation deleted"}


# ── Messages ───────────────────────────────────────────────────


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_messages(conversation_id: str):
    docs = messages_collection.find({"conversation_id": conversation_id}).sort("timestamp", 1)
    return [_serialize_doc(doc) for doc in docs]


@router.post("/chat")
async def chat(payload: MessageCreate):
    """Send a message and get an LLM response. Returns both messages."""
    # Resolve or create conversation
    conversation_id = payload.conversation_id
    if not conversation_id:
        now = datetime.now(timezone.utc)
        conv_result = conversations_collection.insert_one(
            {"title": payload.content[:60], "created_at": now, "updated_at": now}
        )
        conversation_id = str(conv_result.inserted_id)

    now = datetime.now(timezone.utc)

    # Save user message
    user_msg = {
        "conversation_id": conversation_id,
        "role": "user",
        "content": payload.content,
        "timestamp": now,
    }
    msg_result = messages_collection.insert_one(user_msg)
    user_msg["id"] = str(msg_result.inserted_id)

    # Build context from recent messages
    recent = list(
        messages_collection.find({"conversation_id": conversation_id})
        .sort("timestamp", -1)
        .limit(agent_config.MAX_HISTORY)
    )
    context = [
        {"role": m["role"], "content": m["content"]}
        for m in reversed(recent)
    ]

    # Run the agent
    try:
        agent_result = await agent_run(payload.content, context)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Agent request failed: {str(e)}")

    bot_content = agent_result["content"]
    tool_calls = agent_result.get("tool_calls", [])
    mockup_task_id = agent_result.get("mockup_task_id") or None

    # Save assistant message
    bot_msg = {
        "conversation_id": conversation_id,
        "role": "assistant",
        "content": bot_content,
        "timestamp": datetime.now(timezone.utc),
        "mockup_task_id": mockup_task_id,
        "image_url": None,
    }

    # If there's a mockup being generated, append a metadata block
    # so the frontend knows to show a progress bar.
    if mockup_task_id:
        # Append mockup metadata to the bot message content
        bot_msg["content"] = bot_content + (
            f"\n\n<!--MOCKUP task_id={mockup_task_id} -->"
        )

    bot_result = messages_collection.insert_one(bot_msg)
    bot_msg["id"] = str(bot_result.inserted_id)

    # Update conversation timestamp
    conversations_collection.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$set": {"updated_at": datetime.now(timezone.utc)}}
    )

    return {
        "user_message": MessageResponse(**user_msg).model_dump(),
        "bot_message": MessageResponse(**bot_msg).model_dump(),
        "conversation_id": conversation_id,
        "tool_calls": tool_calls,
        "mockup_task_id": mockup_task_id,
    }

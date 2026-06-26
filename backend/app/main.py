from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat, mockup
from app.config import settings

app = FastAPI(title="AI Chat Bot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://ai-packaging-solution-mvp.vercel.app",
        # "https://ai-packaging-solution-mvp-w4g6.vercel.app",
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(mockup.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Chat Bot API is running"}

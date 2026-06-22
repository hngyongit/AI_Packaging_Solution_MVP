import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/chatbot_db")
    LLM_API_URL: str = os.getenv("LLM_API_URL", "http://localhost:11434/api/generate")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret")


settings = Settings()

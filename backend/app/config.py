import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()


def _parse_cloudinary_url(url: str) -> tuple[str, str, str]:
    """Parse cloudinary://api_key:api_secret@cloud_name into parts."""
    if not url:
        return "", "", ""
    try:
        parsed = urlparse(url)
        cloud_name = parsed.hostname or ""
        api_key = parsed.username or ""
        api_secret = parsed.password or ""
        return cloud_name, api_key, api_secret
    except Exception:
        return "", "", ""


class Settings:
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/chatbot_db")
    LLM_API_URL: str = os.getenv("LLM_API_URL", "http://localhost:11434/api/generate")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret")
    LUMICRAFT_API_KEY: str = os.getenv("LUMICRAFT_API_KEY", "")
    MOCKUP_POLL_INTERVAL: int = int(os.getenv("MOCKUP_POLL_INTERVAL", "3"))
    MOCKUP_MAX_POLL_TIME: int = int(os.getenv("MOCKUP_MAX_POLL_TIME", "120"))
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # ── Cloudinary ─────────────────────────────────────────────
    CLOUDINARY_URL: str = os.getenv("CLOUDINARY_URL", "")
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    def __init__(self) -> None:
        if self.CLOUDINARY_URL:
            cn, key, secret = _parse_cloudinary_url(self.CLOUDINARY_URL)
            self.CLOUDINARY_CLOUD_NAME = cn
            self.CLOUDINARY_API_KEY = key
            self.CLOUDINARY_API_SECRET = secret


settings = Settings()
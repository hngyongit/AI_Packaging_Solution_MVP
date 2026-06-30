"""
Route: POST /api/upload/image

Accepts direct image file uploads (multipart/form-data) or an image URL.
Uploads to Cloudinary and returns the secure URL.

The frontend can use this to:
  - Upload a local image file (drag & drop / file picker)
  - Provide a public image URL
"""

import httpx
import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

from app.config import settings

router = APIRouter()

# ── Configure Cloudinary once ──────────────────────────────────
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


class UploadUrlRequest(BaseModel):
    image_url: str


@router.post("/upload/image")
async def upload_image(
    file: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None),
):
    """
    Upload an image to Cloudinary.
    Accepts either:
      - A direct file upload via `file` field (multipart)
      - A public URL via `image_url` field (form data)

    Returns { "url": "...", "public_id": "...", "format": "...", "bytes": ... }
    """
    if file and image_url:
        raise HTTPException(
            status_code=400,
            detail="Provide either a file upload OR an image_url, not both.",
        )

    if not file and not image_url:
        raise HTTPException(
            status_code=400,
            detail="Provide either a file upload (multipart) or an image_url.",
        )

    try:
        # ── Resize & optimise during upload ──────────────────
        # Scale to max 800 px on the longest side + auto quality.
        # This makes the image much smaller & faster for the AI to process.
        transformation = {
            "width": 800,
            "crop": "limit",
            "quality": "auto",
            "fetch_format": "auto",
        }

        if file:
            # ── Upload from file bytes ──────────────────────────
            contents = await file.read()
            result = cloudinary.uploader.upload(
                contents,
                folder="ai_packaging",
                resource_type="image",
                allowed_formats=["png", "jpg", "jpeg", "gif", "webp", "svg"],
                transformation=transformation,
            )
        else:
            # ── Upload from remote URL ──────────────────────────
            result = cloudinary.uploader.upload(
                image_url,
                folder="ai_packaging",
                resource_type="image",
                allowed_formats=["png", "jpg", "jpeg", "gif", "webp", "svg"],
                transformation=transformation,
            )

        return {
            "url": result.get("secure_url") or result.get("url"),
            "public_id": result.get("public_id"),
            "format": result.get("format"),
            "bytes": result.get("bytes"),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload to Cloudinary failed: {str(e)}",
        )

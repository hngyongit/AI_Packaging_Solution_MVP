"""
Tool: generate_mockup

Calls the Lumicraft API to generate a packaging mockup image.
Accepts either a text prompt or a reference image URL + optional prompt.
Uses multipart/form-data for Lumicraft (supports image= + image_2= fields).
Returns a task_id immediately; the backend streams real-time status via SSE
while the frontend shows a progress bar.
"""
import json
import httpx
from tools.base import BaseTool
from app.config import settings


class GenerateMockup(BaseTool):
    """Generate a packaging mockup image using AI."""

    @property
    def name(self) -> str:
        return "generate_mockup"

    @property
    def description(self) -> str:
        return (
            "Generate a visual packaging mockup image. "
            "Use this when the customer wants to see how their packaging design will look "
            "before production. You can accept a reference image URL from the customer. "
            "If the customer provides a link to their logo / artwork, include it as image_url. "
            "You MUST write a detailed prompt describing the box, colors, logo placement, "
            "dimensions, and style."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": (
                        "Detailed English prompt for the AI image generator. "
                        "Describe the packaging mockup in detail: box type (e.g. corrugated box, "
                        "foldable carton, rigid box), colors, logo placement, print style, "
                        "background (always simple white background), lighting, and perspective. "
                        "Example: 'A single corrugated carton box on a simple white background, "
                        "the box has a clean modern logo design on the front in green and white, "
                        "professional product packaging photography, soft studio lighting, "
                        "3D render style.'"
                    ),
                },
                "image_url": {
                    "type": "string",
                    "description": (
                        "Optional. A publicly accessible URL of a reference image "
                        "(e.g. the customer's logo or artwork) to be used as the logo on the box. "
                        "If the customer shared an image link, pass it here. "
                        "The AI will place this artwork onto the packaging mockup."
                    ),
                },
            },
            "required": ["prompt"],
        }

    async def run(self, prompt: str, image_url: str = "") -> str:
        api_key = settings.LUMICRAFT_API_KEY
        if not api_key:
            return json.dumps({
                "status": "error",
                "message": "Lumicraft API key is not configured. Please set LUMICRAFT_API_KEY in .env",
            })

        # Step 1: Build multipart form data
        form_data = {
            "prompt": prompt,
            "model": "C-Image",
            "quality": "hd",
        }

        # If user provided an image URL, download it and attach as file,
        # and also adjust the prompt to reference the uploaded image.
        files = {}
        prompt_suffix = ""
        if image_url:
            try:
                async with httpx.AsyncClient(timeout=15.0) as dl:
                    dl_resp = await dl.get(image_url)
                    if dl_resp.status_code == 200:
                        content_type = dl_resp.headers.get("content-type", "image/png")
                        ext = "png"
                        if "jpeg" in content_type or "jpg" in content_type:
                            ext = "jpg"
                        elif "webp" in content_type:
                            ext = "webp"
                        elif "avif" in content_type:
                            ext = "avif"
                        files["image"] = (f"reference.{ext}", dl_resp.content, content_type)
                        prompt_suffix = (
                            "\n\nThe customer's logo/artwork has been uploaded as 'image'."
                        )
            except Exception:
                # If download fails, fall back to prompt-only generation
                pass

        # Append the image reference hint to the prompt
        if prompt_suffix:
            form_data["prompt"] = prompt + prompt_suffix

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.lumicraft.io/v1/images/generations",
                headers={"Authorization": f"Bearer {api_key}"},
                data=form_data,
                files=files if files else None,
            )

            if resp.status_code == 401:
                return json.dumps({
                    "status": "error",
                    "message": "Invalid or revoked Lumicraft API key.",
                })
            if resp.status_code == 402:
                return json.dumps({
                    "status": "error",
                    "message": "Insufficient Lumicraft credits to generate image.",
                })
            if resp.status_code != 200:
                return json.dumps({
                    "status": "error",
                    "message": f"Image generation API error ({resp.status_code}): {resp.text}",
                })

            data = resp.json()
            task_id = data.get("task_id")
            if not task_id:
                return json.dumps({
                    "status": "error",
                    "message": f"Unexpected response from image API: {data}",
                })

        # Return task info — the backend will stream progress via SSE
        return json.dumps({
            "status": "queued",
            "task_id": task_id,
            "message": "Image generation has been queued.",
        })

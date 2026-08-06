# backend/app/services/gemini_client.py
import os
from google import genai
from google.genai import types
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent / "core"
load_dotenv(BASE_DIR / "login.env")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-lite-latest")
_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


class GeminiConfigurationError(RuntimeError):
    pass


def _get_client() -> genai.Client:
    if _client is None:
        raise GeminiConfigurationError("GEMINI_API_KEY chưa được cấu hình trong app/core/login.env")
    return _client


def ask_gemini(prompt: str, system_instruction: str | None = None, model: str | None = None) -> str:
    """Gọi Gemini API đồng bộ, trả về text response."""
    client = _get_client()
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.2,  # thấp cho tác vụ SQL/phân loại cần chính xác, ổn định
    )
    response = client.models.generate_content(
        model=model or GEMINI_MODEL,
        contents=prompt,
        config=config,
    )
    return response.text or ""


async def ask_gemini_async(prompt: str, system_instruction: str | None = None, model: str | None = None) -> str:
    """Bản async, dùng trong FastAPI route để không block event loop."""
    client = _get_client()
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.2,
    )
    response = await client.aio.models.generate_content(
        model=model or GEMINI_MODEL,
        contents=prompt,
        config=config,
    )
    return response.text or ""
"""Load and validate the Gemini API key."""

import os

from dotenv import load_dotenv

load_dotenv()

PLACEHOLDER_KEYS = {"your_api_key_here", "your_actual_api_key_here"}


def get_gemini_api_key() -> str:
    """Return a configured API key without exposing it in error messages."""
    raw_key = os.getenv("GEMINI_API_KEY")
    if raw_key is None:
        raise RuntimeError("GEMINI_API_KEY environment variable is not configured")

    api_key = raw_key.strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable contains only whitespace")
    if api_key in PLACEHOLDER_KEYS:
        raise RuntimeError("GEMINI_API_KEY is configured with a placeholder value")

    return api_key

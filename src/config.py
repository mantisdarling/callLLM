"""Configuration module for credential validation and runtime environment management."""

import os
from dotenv import load_dotenv

load_dotenv()

PLACEHOLDER_KEY = "your_api_key_here"


def get_gemini_api_key():
    """Retrieve and validate the Gemini API credential from system environment variables.

    Enforces input sanitization ensuring the token is present, non empty,
    and distinct from the repository placeholder string, raising a sanitized
    RuntimeError without leaking token contents into execution traces.
    """
    raw_key = os.getenv("GEMINI_API_KEY")
    if raw_key is None:
        raise RuntimeError("GEMINI_API_KEY environment variable is not configured")

    sanitized_key = raw_key.strip()
    if not sanitized_key:
        raise RuntimeError("GEMINI_API_KEY environment variable contains only whitespace")

    if sanitized_key == PLACEHOLDER_KEY:
        raise RuntimeError("GEMINI_API_KEY is configured with placeholder value")

    return sanitized_key

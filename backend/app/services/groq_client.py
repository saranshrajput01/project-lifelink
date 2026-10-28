"""
Groq client with automatic API key rotation.
(Ported from bizmind-ai.)

When one key hits the rate limit (429), the next key is tried automatically.
With multiple keys, we effectively multiply the daily token quota.
"""

import logging
import threading

from groq import Groq, RateLimitError, APIStatusError

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Thread-safe key index
_lock = threading.Lock()
_current_index = 0


def _get_keys() -> list[str]:
    return settings.groq_api_keys


def _next_key_index(current: int, total: int) -> int:
    return (current + 1) % total


def chat_with_rotation(messages: list[dict], model: str, **kwargs):
    """
    Call Groq chat completions with automatic key rotation on rate limit.
    Tries all available keys before giving up.
    """
    global _current_index

    keys = _get_keys()
    if not keys:
        raise ValueError("No Groq API keys configured")

    total = len(keys)
    attempts = 0

    while attempts < total:
        with _lock:
            idx = _current_index
            key = keys[idx]

        try:
            client = Groq(api_key=key)
            return client.chat.completions.create(
                messages=messages,
                model=model,
                **kwargs,
            )

        except RateLimitError:
            attempts += 1
            with _lock:
                _current_index = _next_key_index(_current_index, total)
                key_num = _current_index + 1
            logger.warning(
                f"[GROQ] Key #{idx+1} rate limited — rotating to key #{key_num}"
            )

        except APIStatusError as e:
            if e.status_code == 429:
                attempts += 1
                with _lock:
                    _current_index = _next_key_index(_current_index, total)
                logger.warning(
                    f"[GROQ] Key #{idx+1} quota hit — rotating to key #{_current_index+1}"
                )
            else:
                raise

    raise RateLimitError(
        f"All {total} Groq API keys are rate limited.",
        response=None,
        body=None,
    )

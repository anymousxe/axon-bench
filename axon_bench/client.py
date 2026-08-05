"""Minimal OpenAI-compatible chat client — stdlib only, no dependencies."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request


class BenchError(RuntimeError):
    pass


def chat_completion(
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    *,
    temperature: float = 0.0,
    max_tokens: int = 2048,
    timeout: float = 180.0,
    retries: int = 3,
) -> str:
    """POST one chat completion and return the assistant text.

    base_url must be the OpenAI-compatible root, e.g.
    ``https://api.openai.com/v1`` — ``/chat/completions`` is appended.
    """
    url = base_url.rstrip("/") + "/chat/completions"
    payload = json.dumps(
        {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode("utf-8")

    last_error: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "content-type": "application/json",
                "authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as res:
                body = json.loads(res.read().decode("utf-8"))
            choices = body.get("choices") or []
            if not choices:
                raise BenchError(f"empty choices in response: {body}")
            return choices[0].get("message", {}).get("content", "") or ""
        except urllib.error.HTTPError as error:
            last_error = error
            if error.code in (429, 500, 502, 503, 529) and attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            detail = error.read().decode("utf-8", "replace")[:300]
            raise BenchError(f"HTTP {error.code}: {detail}") from error
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            last_error = error
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            raise BenchError(f"request failed: {error}") from error
    raise BenchError(f"request failed after retries: {last_error}")

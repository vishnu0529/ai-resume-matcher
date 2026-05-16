import json
import logging
import re
from typing import Any
from app.core.config import settings

logger = logging.getLogger(__name__)

def call_llm(system: str, user: str, max_tokens: int = 2048) -> str:
    provider = settings.LLM_PROVIDER.lower()
    if provider == "google":
        from google import genai
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        prompt = f"{system}\n\n{user}"
        response = client.models.generate_content(
            model=settings.LLM_MODEL,
            contents=prompt,
        )
        return response.text
    elif provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return msg.content[0].text
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}")

def call_llm_json(system: str, user: str, max_tokens: int = 2048) -> dict[str, Any]:
    raw = call_llm(system, user + "\n\nRespond ONLY with valid JSON. No markdown, no prose.", max_tokens)
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error("JSON parse failed. Raw response:\n%s", raw)
        raise ValueError(f"LLM returned invalid JSON: {exc}") from exc

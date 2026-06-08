"""Natural language intent detection for extracting actionable items from chat.

Supports two intents:
- CREATE_NOTE: "Save a note: ...", "Note that ...", "Remember this: ..."
- CREATE_REMINDER: "Remind me to ...", "Reminder: ... on Friday", "Don't forget to ..."

When no OpenAI key is configured, uses regex-based extraction.
With an OpenAI key, uses the LLM for more accurate intent parsing.
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from openai import AsyncOpenAI

from app.core.config import Settings


@dataclass
class DetectedIntent:
    intent: str  # "create_note", "create_reminder", "none"
    title: str = ""
    body: str = ""
    due_at: datetime | None = None
    priority: int = 0
    confidence: float = 0.0
    extra: dict = field(default_factory=dict)


# ── Regex patterns for local (no-API-key) detection ─────────


_NOTE_PATTERNS = [
    re.compile(r"(?:save\s+a?\s*note|note\s+(?:that|this|down))[\s:]+(.+)", re.IGNORECASE),
    re.compile(r"(?:remember\s+(?:that|this))[\s:]+(.+)", re.IGNORECASE),
    re.compile(r"(?:jot\s+down|write\s+down)[\s:]+(.+)", re.IGNORECASE),
]

_REMINDER_PATTERNS = [
    re.compile(
        r"(?:remind\s+me\s+to|reminder[\s:]+|don'?t\s+(?:let\s+me\s+)?forget\s+to)[\s:]*(.+)",
        re.IGNORECASE,
    ),
    re.compile(r"(?:set\s+a?\s*reminder)[\s:]+(.+)", re.IGNORECASE),
]


def _detect_locally(message: str) -> DetectedIntent:
    """Regex-based intent detection (no LLM needed)."""
    for pattern in _NOTE_PATTERNS:
        match = pattern.search(message)
        if match:
            content = match.group(1).strip().rstrip(".")
            # Try to split into title and body at the first sentence boundary
            parts = re.split(r"[.!]\s+", content, maxsplit=1)
            title = parts[0][:255]
            body = parts[1] if len(parts) > 1 else ""
            return DetectedIntent(
                intent="create_note",
                title=title,
                body=body,
                confidence=0.75,
            )

    for pattern in _REMINDER_PATTERNS:
        match = pattern.search(message)
        if match:
            content = match.group(1).strip().rstrip(".")
            return DetectedIntent(
                intent="create_reminder",
                title=content[:255],
                confidence=0.75,
            )

    return DetectedIntent(intent="none", confidence=1.0)


# ── LLM-based intent detection ──────────────────────────────

_SYSTEM_PROMPT = """You are an intent classifier for a personal assistant called Life-OS.
Given a user message, determine if the user wants to:
1. Create a note (save information for later)
2. Create a reminder (be reminded about something, possibly at a specific time)
3. Neither (just chatting)

Respond with ONLY a JSON object (no markdown, no explanation):
{
  "intent": "create_note" | "create_reminder" | "none",
  "title": "short title extracted from the message",
  "body": "additional details if any, empty string otherwise",
  "due_at": "ISO 8601 datetime if mentioned, null otherwise",
  "priority": 0-3 (0=low, 1=normal, 2=high, 3=urgent),
  "confidence": 0.0-1.0
}"""


async def _detect_with_llm(message: str, client: AsyncOpenAI, model: str) -> DetectedIntent:
    """LLM-based intent detection for higher accuracy."""
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            temperature=0.1,
            max_tokens=256,
        )
        raw = response.choices[0].message.content or "{}"
        # Strip markdown code fences if present
        raw = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`")
        data = json.loads(raw)
        due_at = None
        if data.get("due_at"):
            try:
                due_at = datetime.fromisoformat(data["due_at"])
                if due_at.tzinfo is None:
                    due_at = due_at.replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                pass
        return DetectedIntent(
            intent=data.get("intent", "none"),
            title=data.get("title", "")[:255],
            body=data.get("body", ""),
            due_at=due_at,
            priority=min(max(int(data.get("priority", 0)), 0), 3),
            confidence=float(data.get("confidence", 0.8)),
        )
    except Exception:
        # Fall back to local detection on any LLM error
        return _detect_locally(message)


class IntentDetector:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        has_key = bool(settings.openai_api_key and settings.openai_api_key.strip())
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if has_key else None

    async def detect(self, message: str) -> DetectedIntent:
        if self.client:
            return await _detect_with_llm(message, self.client, self.settings.openai_chat_model)
        return _detect_locally(message)

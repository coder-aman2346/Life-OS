import hashlib
import re

from openai import AsyncOpenAI

from app.core.config import Settings
from app.schemas.memory import MemoryContext


def _has_api_key(settings: Settings) -> bool:
    return bool(settings.openai_api_key and settings.openai_api_key.strip())


class EmbeddingService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = (
            AsyncOpenAI(api_key=settings.openai_api_key) if _has_api_key(settings) else None
        )

    async def embed(self, text: str) -> list[float]:
        if self.client:
            response = await self.client.embeddings.create(
                model=self.settings.openai_embedding_model,
                input=text,
            )
            return list(response.data[0].embedding)

        digest = hashlib.sha256(text.lower().encode("utf-8")).digest()
        values: list[float] = []
        for index in range(1536):
            byte = digest[index % len(digest)]
            values.append((byte / 127.5) - 1.0)
        return values


class SummarizerService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = (
            AsyncOpenAI(api_key=settings.openai_api_key) if _has_api_key(settings) else None
        )

    async def summarize(self, messages: list[dict]) -> str:
        if not messages:
            return ""

        if self.client:
            transcript = "\n".join(f"{item['role']}: {item['content']}" for item in messages)
            response = await self.client.chat.completions.create(
                model=self.settings.openai_summary_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Extract durable user facts, preferences, goals, and constraints. "
                            "Return concise bullet points only."
                        ),
                    },
                    {"role": "user", "content": transcript},
                ],
            )
            return response.choices[0].message.content or ""

        return self._summarize_locally(messages)

    def _summarize_locally(self, messages: list[dict]) -> str:
        facts: list[str] = []
        user_text = " ".join(
            item["content"] for item in messages if item.get("role") == "user"
        ).strip()

        name_match = re.search(r"\bmy name is ([A-Z][a-zA-Z0-9_-]+)", user_text, re.IGNORECASE)
        if name_match:
            facts.append(f"User's name is {name_match.group(1).strip()}.")

        like_match = re.search(r"\bi like ([^.!,;]+)", user_text, re.IGNORECASE)
        if like_match:
            facts.append(f"User likes {like_match.group(1).strip()}.")

        prefer_match = re.search(r"\bi prefer ([^.!,;]+)", user_text, re.IGNORECASE)
        if prefer_match:
            facts.append(f"User prefers {prefer_match.group(1).strip()}.")

        if facts:
            return "\n".join(f"- {fact}" for fact in facts)
        return f"- Recent conversation summary: {user_text[:500]}"


class ChatModelService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = (
            AsyncOpenAI(api_key=settings.openai_api_key) if _has_api_key(settings) else None
        )

    async def complete(self, *, message: str, context: MemoryContext) -> str:
        system_prompt = format_context_toon(context)

        if self.client:
            response = await self.client.chat.completions.create(
                model=self.settings.openai_chat_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
            )
            return response.choices[0].message.content or ""

        if context.long_term:
            remembered = "; ".join(
                fragment.content.replace("\n", " ") for fragment in context.long_term[:2]
            )
            return f"I remember this about you: {remembered} You said: {message}"
        return f"I do not have long-term memories for you yet. You said: {message}"


def format_context_toon(context: MemoryContext) -> str:
    recent = "\n".join(
        f"{item.get('role', 'unknown')}: {item.get('content', '')}" for item in context.recent
    )
    facts = "\n".join(f"- {fragment.content}" for fragment in context.long_term)
    return f"""You are a persistent assistant. You remember the user across sessions.

[SESSION_RECENT]
{recent}
[/SESSION_RECENT]

[USER_FACTS]
{facts}
[/USER_FACTS]
"""

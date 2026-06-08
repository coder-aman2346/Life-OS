import json
from collections import defaultdict
from time import time
from typing import Protocol

from redis.asyncio import Redis
import structlog


class ShortTermMemoryProtocol(Protocol):
    async def append(self, message: dict) -> None: ...
    async def get_history(self, last_n: int = 20) -> list[dict]: ...
    async def clear(self) -> None: ...
    async def set_ttl(self, seconds: int) -> None: ...


class ShortTermMemory:
    def __init__(
        self,
        redis: Redis,
        session_id: str,
        *,
        ttl: int = 3600,
        max_messages: int = 20,
    ) -> None:
        self.redis = redis
        self.key = f"session:{session_id}:messages"
        self.ttl = ttl
        self.max_messages = max_messages
        self._in_memory = InMemoryShortTermMemory(session_id, ttl=ttl, max_messages=max_messages)
        self._use_in_memory = False

    async def append(self, message: dict) -> None:
        if self._use_in_memory:
            await self._in_memory.append(message)
            return
        try:
            await self.redis.lpush(self.key, json.dumps(message))
            await self.redis.ltrim(self.key, 0, self.max_messages - 1)
            await self.set_ttl(self.ttl)
        except Exception as e:
            structlog.get_logger().warning(
                "Redis error, falling back to InMemoryShortTermMemory", error=str(e)
            )
            self._use_in_memory = True
            await self._in_memory.append(message)

    async def get_history(self, last_n: int = 20) -> list[dict]:
        if self._use_in_memory:
            return await self._in_memory.get_history(last_n)
        try:
            raw_messages = await self.redis.lrange(self.key, 0, last_n - 1)
            messages = [
                json.loads(item.decode("utf-8") if isinstance(item, bytes) else item)
                for item in raw_messages
            ]
            return list(reversed(messages))
        except Exception as e:
            structlog.get_logger().warning(
                "Redis error, falling back to InMemoryShortTermMemory", error=str(e)
            )
            self._use_in_memory = True
            return await self._in_memory.get_history(last_n)

    async def clear(self) -> None:
        if self._use_in_memory:
            await self._in_memory.clear()
            return
        try:
            await self.redis.delete(self.key)
        except Exception as e:
            structlog.get_logger().warning(
                "Redis error, falling back to InMemoryShortTermMemory", error=str(e)
            )
            self._use_in_memory = True
            await self._in_memory.clear()

    async def set_ttl(self, seconds: int) -> None:
        if self._use_in_memory:
            await self._in_memory.set_ttl(seconds)
            return
        try:
            await self.redis.expire(self.key, seconds)
        except Exception as e:
            structlog.get_logger().warning(
                "Redis error, falling back to InMemoryShortTermMemory", error=str(e)
            )
            self._use_in_memory = True
            await self._in_memory.set_ttl(seconds)


# Module-level shared store so multiple InMemoryShortTermMemory instances
# for the same session_id see the same data (mimics Redis behaviour).
_in_memory_store: dict[str, list[dict]] = defaultdict(list)
_in_memory_ttl: dict[str, float] = {}


class InMemoryShortTermMemory:
    def __init__(self, session_id: str, *, ttl: int = 3600, max_messages: int = 20) -> None:
        self.key = f"session:{session_id}:messages"
        self.ttl = ttl
        self.max_messages = max_messages

    async def append(self, message: dict) -> None:
        _in_memory_store[self.key].insert(0, message)
        _in_memory_store[self.key] = _in_memory_store[self.key][: self.max_messages]
        await self.set_ttl(self.ttl)

    async def get_history(self, last_n: int = 20) -> list[dict]:
        if _in_memory_ttl.get(self.key, time() + 1) < time():
            await self.clear()
            return []
        return list(reversed(_in_memory_store[self.key][:last_n]))

    async def clear(self) -> None:
        _in_memory_store.pop(self.key, None)
        _in_memory_ttl.pop(self.key, None)

    async def set_ttl(self, seconds: int) -> None:
        _in_memory_ttl[self.key] = time() + seconds

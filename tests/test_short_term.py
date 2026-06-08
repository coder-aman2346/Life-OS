import pytest

from app.memory.short_term import InMemoryShortTermMemory


@pytest.mark.anyio
async def test_short_term_memory_keeps_recent_messages_in_order() -> None:
    memory = InMemoryShortTermMemory("session-1", max_messages=3)

    await memory.append({"role": "user", "content": "one"})
    await memory.append({"role": "assistant", "content": "two"})
    await memory.append({"role": "user", "content": "three"})
    await memory.append({"role": "assistant", "content": "four"})

    assert await memory.get_history(last_n=3) == [
        {"role": "assistant", "content": "two"},
        {"role": "user", "content": "three"},
        {"role": "assistant", "content": "four"},
    ]

    await memory.clear()
    assert await memory.get_history() == []

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_long_term_memory
from app.memory.long_term import LongTermMemory
from app.schemas.memory import MemoryFragmentRead

router = APIRouter(prefix="/users", tags=["memory"])


@router.get("/{user_id}/memory", response_model=list[MemoryFragmentRead])
def get_user_memory(
    user_id: str,
    long_term: Annotated[LongTermMemory, Depends(get_long_term_memory)],
) -> list[MemoryFragmentRead]:
    return long_term.list_fragments(user_id)


@router.delete("/{user_id}/memory")
def forget_user_memory(
    user_id: str,
    long_term: Annotated[LongTermMemory, Depends(get_long_term_memory)],
) -> dict[str, int]:
    deleted = long_term.forget_user_memory(user_id)
    return {"deleted": deleted}

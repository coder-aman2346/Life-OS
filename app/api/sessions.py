from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status

from app.api.dependencies import get_chat_service, get_long_term_memory, get_memory_router
from app.memory.long_term import LongTermMemory, SessionNotFoundError
from app.memory.router import MemoryRouter
from app.schemas.memory import ChatRequest, ChatResponse, MessageRead, SessionCreate, SessionRead
from app.services.chat_service import ChatService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionRead, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreate,
    long_term: Annotated[LongTermMemory, Depends(get_long_term_memory)],
) -> SessionRead:
    return long_term.create_session(payload.user_id)


@router.post("/{session_id}/chat", response_model=ChatResponse)
async def chat(
    session_id: str,
    payload: ChatRequest,
    service: Annotated[ChatService, Depends(get_chat_service)],
) -> ChatResponse:
    try:
        return await service.chat(
            session_id=session_id,
            user_id=payload.user_id,
            message=payload.message,
        )
    except SessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        ) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.get("/{session_id}/history", response_model=list[MessageRead])
def get_history(
    session_id: str,
    long_term: Annotated[LongTermMemory, Depends(get_long_term_memory)],
) -> list[MessageRead]:
    try:
        return long_term.get_history(session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        ) from exc


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def end_session(
    session_id: str,
    user_id: str,
    long_term: Annotated[LongTermMemory, Depends(get_long_term_memory)],
    memory_router: Annotated[MemoryRouter, Depends(get_memory_router)],
) -> None:
    try:
        session = long_term.get_session(session_id)
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Session does not belong to user",
            )
        await memory_router.consolidate(session_id, user_id)
        long_term.delete_session(session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        ) from exc


@router.websocket("/{session_id}/chat/ws")
async def chat_ws(
    websocket: WebSocket,
    session_id: str,
    user_id: str,
    service: Annotated[ChatService, Depends(get_chat_service)],
) -> None:
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            response = await service.chat(session_id=session_id, user_id=user_id, message=message)
            await websocket.send_json(response.model_dump())
    except WebSocketDisconnect:
        return

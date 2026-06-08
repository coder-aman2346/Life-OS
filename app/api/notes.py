from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_note_service
from app.schemas.notes_reminders import NoteCreate, NoteRead, NoteUpdate
from app.services.note_service import NoteNotFoundError, NoteService

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(
    payload: NoteCreate,
    service: Annotated[NoteService, Depends(get_note_service)],
) -> NoteRead:
    return service.create(payload)


@router.get("", response_model=list[NoteRead])
def list_notes(
    user_id: str,
    service: Annotated[NoteService, Depends(get_note_service)],
    q: str | None = Query(default=None, description="Search query"),
) -> list[NoteRead]:
    if q:
        return service.search(user_id, q)
    return service.list_by_user(user_id)


@router.get("/{note_id}", response_model=NoteRead)
def get_note(
    note_id: str,
    service: Annotated[NoteService, Depends(get_note_service)],
) -> NoteRead:
    try:
        return service.get(note_id)
    except NoteNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")


@router.patch("/{note_id}", response_model=NoteRead)
def update_note(
    note_id: str,
    payload: NoteUpdate,
    service: Annotated[NoteService, Depends(get_note_service)],
) -> NoteRead:
    try:
        return service.update(note_id, payload)
    except NoteNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: str,
    service: Annotated[NoteService, Depends(get_note_service)],
) -> None:
    try:
        service.delete(note_id)
    except NoteNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

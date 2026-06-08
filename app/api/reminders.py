from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_reminder_service
from app.schemas.notes_reminders import ReminderCreate, ReminderRead, ReminderUpdate
from app.services.reminder_service import ReminderNotFoundError, ReminderService

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post("", response_model=ReminderRead, status_code=status.HTTP_201_CREATED)
def create_reminder(
    payload: ReminderCreate,
    service: Annotated[ReminderService, Depends(get_reminder_service)],
) -> ReminderRead:
    return service.create(payload)


@router.get("", response_model=list[ReminderRead])
def list_reminders(
    user_id: str,
    service: Annotated[ReminderService, Depends(get_reminder_service)],
    include_completed: bool = Query(default=False),
) -> list[ReminderRead]:
    return service.list_by_user(user_id, include_completed=include_completed)


@router.get("/due", response_model=list[ReminderRead])
def get_due_reminders(
    user_id: str,
    service: Annotated[ReminderService, Depends(get_reminder_service)],
) -> list[ReminderRead]:
    return service.get_due_soon(user_id)


@router.get("/{reminder_id}", response_model=ReminderRead)
def get_reminder(
    reminder_id: str,
    service: Annotated[ReminderService, Depends(get_reminder_service)],
) -> ReminderRead:
    try:
        return service.get(reminder_id)
    except ReminderNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")


@router.patch("/{reminder_id}", response_model=ReminderRead)
def update_reminder(
    reminder_id: str,
    payload: ReminderUpdate,
    service: Annotated[ReminderService, Depends(get_reminder_service)],
) -> ReminderRead:
    try:
        return service.update(reminder_id, payload)
    except ReminderNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(
    reminder_id: str,
    service: Annotated[ReminderService, Depends(get_reminder_service)],
) -> None:
    try:
        service.delete(reminder_id)
    except ReminderNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

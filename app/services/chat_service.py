from langgraph.graph.state import CompiledStateGraph

from app.memory.long_term import LongTermMemory
from app.memory.router import MemoryRouter
from app.schemas.memory import ChatResponse
from app.services.ai import ChatModelService
from app.services.intent_detector import IntentDetector
from app.services.note_service import NoteService
from app.services.reminder_service import ReminderService
from app.schemas.notes_reminders import NoteCreate, ReminderCreate


class ChatService:
    def __init__(
        self,
        *,
        long_term: LongTermMemory,
        memory_router: MemoryRouter,
        chat_model: ChatModelService,
        agent_graph: CompiledStateGraph,
        intent_detector: IntentDetector,
        note_service: NoteService | None = None,
        reminder_service: ReminderService | None = None,
        consolidation_turn_threshold: int,
    ) -> None:
        self.long_term = long_term
        self.memory_router = memory_router
        self.chat_model = chat_model
        self.agent_graph = agent_graph
        self.intent_detector = intent_detector
        self.note_service = note_service
        self.reminder_service = reminder_service
        self.consolidation_turn_threshold = consolidation_turn_threshold
        # Track turn counts per session to avoid relying on bounded STM length.
        self._turn_counts: dict[str, int] = {}

    async def chat(self, *, session_id: str, user_id: str, message: str) -> ChatResponse:
        session = self.long_term.get_session(session_id)
        if session.user_id != user_id:
            raise PermissionError("Session does not belong to user")

        # Detect intent (note / reminder / none) from the user message.
        intent = await self.intent_detector.detect(message)
        action_taken = None

        if intent.intent == "create_note" and intent.confidence >= 0.6 and self.note_service:
            note = self.note_service.create(
                NoteCreate(
                    user_id=user_id,
                    title=intent.title or "Untitled Note",
                    body=intent.body,
                )
            )
            action_taken = f'📝 Note saved: "{note.title}"'

        elif (
            intent.intent == "create_reminder"
            and intent.confidence >= 0.6
            and self.reminder_service
        ):
            reminder = self.reminder_service.create(
                ReminderCreate(
                    user_id=user_id,
                    title=intent.title or "Untitled Reminder",
                    due_at=intent.due_at,
                    priority=intent.priority,
                )
            )
            action_taken = f'⏰ Reminder created: "{reminder.title}"'

        # Run the LangGraph agent: retrieve memory → call LLM → update memory.
        result = await self.agent_graph.ainvoke(
            {
                "session_id": session_id,
                "user_id": user_id,
                "user_message": message,
                "memory_context": None,
                "response": "",
            }
        )

        response = result["response"]
        context = result["memory_context"]

        # Prepend the action confirmation to the LLM response.
        if action_taken:
            response = f"{action_taken}\n\n{response}"

        # Increment turn count and consolidate when threshold is reached.
        self._turn_counts[session_id] = self._turn_counts.get(session_id, 0) + 1
        if self._turn_counts[session_id] >= self.consolidation_turn_threshold:
            await self.memory_router.consolidate(session_id, user_id)
            self._turn_counts[session_id] = 0

        return ChatResponse(
            session_id=session_id,
            response=response,
            used_long_term_memory=(
                [fragment.content for fragment in context.long_term] if context else []
            ),
        )

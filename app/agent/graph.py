from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.memory.router import MemoryRouter
from app.schemas.memory import MemoryContext
from app.services.ai import ChatModelService


class AgentState(TypedDict):
    session_id: str
    user_id: str
    user_message: str
    memory_context: MemoryContext
    response: str


def build_graph(memory_router: MemoryRouter, chat_model: ChatModelService):
    """Build the LangGraph agent: retrieve memory → call LLM → update memory."""

    async def retrieve_memory_node(state: AgentState) -> AgentState:
        state["memory_context"] = await memory_router.get_context(
            state["session_id"],
            state["user_id"],
            state["user_message"],
        )
        return state

    async def call_llm_node(state: AgentState) -> AgentState:
        state["response"] = await chat_model.complete(
            message=state["user_message"],
            context=state["memory_context"],
        )
        return state

    async def update_memory_node(state: AgentState) -> AgentState:
        await memory_router.append_turn(
            state["session_id"],
            state["user_message"],
            state["response"],
        )
        return state

    graph = StateGraph(AgentState)
    graph.add_node("retrieve_memory", retrieve_memory_node)
    graph.add_node("call_llm", call_llm_node)
    graph.add_node("update_memory", update_memory_node)
    graph.set_entry_point("retrieve_memory")
    graph.add_edge("retrieve_memory", "call_llm")
    graph.add_edge("call_llm", "update_memory")
    graph.add_edge("update_memory", END)
    return graph.compile()

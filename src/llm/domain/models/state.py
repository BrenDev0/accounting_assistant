from typing_extensions import TypedDict
from typing import List, Any, Dict
from uuid import UUID
from expertise_chats.broker import InteractionEvent
from src.llm.domain.models.orchestrator import OrchestratorResponse


class State(TypedDict):
    orchestrator_response: OrchestratorResponse
    final_response: str
    event: InteractionEvent
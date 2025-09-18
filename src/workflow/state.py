from typing_extensions import TypedDict
from uuid import UUID
from sqlalchemy.orm import Session
from src.workflow.agents.orchestrator.orchestrator_models import OrchestratorResponse

class State(TypedDict):
    user_id: UUID
    company_id: UUID
    input: str
    db: Session
    orchestrator_response: OrchestratorResponse
    accounting_assistant_response: str
    data_assistant_response: str
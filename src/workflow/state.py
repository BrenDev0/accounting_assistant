from typing_extensions import TypedDict
from uuid import UUID
from sqlalchemy.orm import Session

class State(TypedDict):
    user_id: UUID
    company_id: UUID
    input: str
    db: Session
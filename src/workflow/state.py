from pydantic import BaseModel
from typing_extensions import TypedDict
from uuid import UUID

class State(TypedDict):
    user_id: UUID
    company_id: UUID
    input: str
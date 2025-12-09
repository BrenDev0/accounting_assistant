from pydantic import BaseModel
from typing import Optional

class DataAssistantResponse(BaseModel):
    sql: Optional[str] = None
    error: Optional[str] = None
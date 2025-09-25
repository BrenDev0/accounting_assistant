from pydantic import BaseModel
from typing import Optional

class DataAssistantRespone(BaseModel):
    sql: Optional[str] = None
    error: Optional[str] = None
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
from uuid import UUID

class InteractionRequest(BaseModel):
    input: str
    chat_id: UUID
    company_id: UUID
    chat_history: List[Dict[str, Any]]
    user_id: UUID

class  InteractionResponse(BaseModel):
    response: Union[str, List[Any]]
from dotenv import load_dotenv
load_dotenv()
import pytest
import os 
from src.workflow.state import State
from src.database.database import get_db_session
from  src.workflow.services.embedding_service import EmbeddingService
from src.workflow.services.llm_service import LlmService
from src.workflow.services.prompt_service import PromptService
from src.workflow.agents.data_assistant.data_assistant import DataAssistant
from src.api.core.services.redis_service import RedisService


@pytest.mark.asyncio
async def test_data_assistant():
    db = next(get_db_session())
    state = State(
        user_id="",
        company_id=os.getenv("TEST_COMPANY_ID"),
        db=db,
        input="show total bikes rented in summer as summer rentals "
        "in winter as winter rentals "
        "in spring as spring rentals "
        "in autumn as fall rentals"
        "and the percentage of total bikes rented represented by the seasons as percentage"
    )
    
    redis_service = RedisService()
    
    embedding_service = EmbeddingService()
    
    prompt_service = PromptService(
        embedding_service=embedding_service, 
        redis_service=redis_service
    )
    
    llm_service =  LlmService()
    
    data_assistant = DataAssistant(
        prompt_service=prompt_service,
        llm_service=llm_service
    )

    res = await data_assistant.interact(state=state)

    print(res, "RESPONSE:::::::::::::::::::::")
    assert res

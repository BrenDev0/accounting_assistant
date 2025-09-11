from dotenv import load_dotenv
load_dotenv()
import pytest
from src.workflow.agents.spreadsheet_builder.prompted_spreadsheet_builder import PromptedSpreadsheetBuilder
from src.workflow.services.llm_service import LlmService
from src.workflow.services.prompt_service import PromptService
from src.workflow.services.embedding_service import EmbeddingService
from src.api.core.services.redis_service import RedisService
from src.workflow.state import State
import asyncio
import os 


builder = PromptedSpreadsheetBuilder(
    llm_service=LlmService(),
    prompt_service=PromptService(
        embedding_service=EmbeddingService(),
        redis_service=RedisService()
    )
)

state = State(
    user_id=os.getenv("TEST_USER_ID"),
    company_id=os.getenv("TEST_COMPANY_ID"),
    input="make me a spreadsheet showing how many bikes a rented and  the season they were rented in"
)


@pytest.mark.asyncio
async def test_interaction():
    result = await builder.interact(state)
    print("LLM Response:", result)
    assert isinstance(result, str)
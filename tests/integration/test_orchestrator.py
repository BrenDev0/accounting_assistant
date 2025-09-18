from dotenv import load_dotenv
load_dotenv()
import pytest
import os 
from src.workflow.state import State
from src.database.database import get_db_session
from  src.workflow.services.embedding_service import EmbeddingService
from src.workflow.services.llm_service import LlmService
from src.workflow.services.prompt_service import PromptService
from src.workflow.agents.orchestrator.orchestrator import Orchestrator
from src.workflow.agents.orchestrator.orchestrator_models import OrchestratorResponse
from src.api.core.services.redis_service import RedisService

redis_service = RedisService()
    
embedding_service = EmbeddingService()

prompt_service = PromptService(
    embedding_service=embedding_service, 
    redis_service=redis_service
)

llm_service =  LlmService()

orchestrator = Orchestrator(
    prompt_service=prompt_service,
    llm_service=llm_service
)



@pytest.mark.asyncio
async def test_data_vis_true():
    db = next(get_db_session())
    input = """show total bikes rented in summer as summer rentals 
        in winter as winter rentals 
        in spring as spring rentals 
        in autumn as fall rentals
        and the percentage of total bikes rented represented by the seasons as percentage"""
    state = State(
        user_id="",
        company_id=os.getenv("TEST_COMPANY_ID"),
        db=db,
        input=input
    )

    res: OrchestratorResponse = await orchestrator.interact(state=state)

    assert res.general_accounting == False
    assert res.document_specific_data == True
    assert res.data_visualization ==True

@pytest.mark.asyncio
async def test_data_vis_false():
    db = next(get_db_session())
    input = """
    what was the total number of bikes rented when rainfal was greater than 0?
    """
    state = State(
        user_id="",
        company_id=os.getenv("TEST_COMPANY_ID"),
        db=db,
        input=input
    )
    
    res: OrchestratorResponse = await orchestrator.interact(state=state)

    assert res.general_accounting == False
    assert res.document_specific_data == True
    assert res.data_visualization ==False


@pytest.mark.asyncio
async def test_data_gen_accoutning_true():
    db = next(get_db_session())
    input = """
    what is good will on a balance sheet?
    """
    state = State(
        user_id="",
        company_id=os.getenv("TEST_COMPANY_ID"),
        db=db,
        input=input
    )
    
    res: OrchestratorResponse = await orchestrator.interact(state=state)

    assert res.general_accounting == True
    assert res.document_specific_data == False
    assert res.data_visualization == False




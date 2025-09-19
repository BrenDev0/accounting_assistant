from dotenv import load_dotenv
load_dotenv()
import os
import pytest
from uuid import uuid4
from src.workflow.graph import create_graph
from src.workflow.state import State
from src.database.database import get_db_session
from src.dependencies.configure_container import configure_container

configure_container()

@pytest.mark.asyncio
async def test_graph_accounting_assistant_path():
    db = next(get_db_session())
    state = {
        "user_id": os.getenv("TEST_USER_ID"),
        "company_id": os.getenv("TEST_COMPANY_ID"),
        "input": "What is double-entry bookkeeping?",
        "db": db,  
        "orchestrator_response": None,
        "accounting_assistant_response": None,
        "data_assistant_response": None,
    }

    graph = create_graph()
    result = await graph.ainvoke(state)
    
    assert "accounting_assistant_response" in result
    assert result["accounting_assistant_response"] is not None
    print("Accounting Assistant Response:", result["accounting_assistant_response"])

@pytest.mark.asyncio
async def test_graph_data_assistant_path():
    db = next(get_db_session())
    state = {
        "user_id": os.getenv("TEST_USER_ID"),
        "company_id": os.getenv("TEST_COMPANY_ID"),
        "input": "Show total bike rentals when rainfall was greater than 0.",
        "db": db,
        "orchestrator_response": None,
        "accounting_assistant_response": None,
        "data_assistant_response": None,
    }

    graph = create_graph()
    result = await graph.ainvoke(state)
    assert "data_assistant_response" in result
    assert result["data_assistant_response"] is not None
    print("Data Assistant Response:", result["data_assistant_response"])
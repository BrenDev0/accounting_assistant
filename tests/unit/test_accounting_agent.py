import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.workflow.agents.accounting_assistant.accounting_assistant import AccountingAssistant
from src.workflow.state import State

@pytest.fixture
def mock_llm_service():
    return MagicMock()

@pytest.fixture
def mock_prompt_service():
    return MagicMock()

@pytest.fixture
def agent(mock_llm_service, mock_prompt_service):
    return AccountingAssistant(mock_llm_service, mock_prompt_service)

@pytest.fixture
def state():
    return {
        "user_id": str(uuid4()),
        "company_id": str(uuid4()),
        "input": "What is double-entry bookkeeping?"
    }

@pytest.mark.asyncio
async def test_interact_calls_prompt_and_llm(agent, mock_llm_service, mock_prompt_service, state):
    # Mock prompt and llm chain
    mock_prompt = MagicMock()
    mock_llm = MagicMock()
    mock_chain = MagicMock()
    mock_chain.ainvoke = AsyncMock(return_value=MagicMock(content="Test response"))
    mock_prompt.__or__ = MagicMock(return_value=mock_chain)
    mock_llm_service.get_llm.return_value = mock_llm
    mock_prompt_service.custom_prompt_template = AsyncMock(return_value=mock_prompt)

    # Patch __get_prompt_template to use the real async method
    # (no need to patch, since it's async in the implementation)

    result = await agent.interact(state)

    mock_llm_service.get_llm.assert_called_once_with(temperature=0.2, max_tokens=250)
    mock_prompt_service.custom_prompt_template.assert_awaited_once()
    mock_chain.ainvoke.assert_awaited_once_with({"input": state["input"]})
    assert result == "Test response"

def test_init_sets_services(mock_llm_service, mock_prompt_service):
    agent = AccountingAssistant(mock_llm_service, mock_prompt_service)
    assert agent._AccountingAssistant__llm_service is mock_llm_service
    assert agent._AccountingAssistant__prompt_service is mock_prompt_service
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.workflow.agents.spreadsheet_builder.prompted_spreadsheet_builder import PromptedSpreadsheetBuilder

@pytest.fixture
def mock_llm_service():
    return MagicMock()

@pytest.fixture
def mock_prompt_service():
    return MagicMock()

@pytest.fixture
def builder(mock_llm_service, mock_prompt_service):
    return PromptedSpreadsheetBuilder(mock_llm_service, mock_prompt_service)

@pytest.fixture
def state():
    return {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "company_id": "123e4567-e89b-12d3-a456-426614174001",
        "input": "List all taxes paid and their dates."
    }

@pytest.mark.asyncio
async def test_interact_calls_prompt_and_llm(builder, mock_llm_service, mock_prompt_service, state):
    # Mock prompt and llm chain
    mock_prompt = MagicMock()
    mock_llm = MagicMock()
    mock_chain = MagicMock()
    mock_chain.ainvoke = AsyncMock(return_value=MagicMock(content="Test structured response"))
    mock_prompt.__or__ = MagicMock(return_value=mock_chain)
    mock_llm_service.get_llm.return_value = mock_llm
    mock_prompt_service.custom_prompt_template = AsyncMock(return_value=mock_prompt)

    result = await builder.interact(state)

    mock_llm_service.get_llm.assert_called_once_with(temperature=0.2, max_tokens=350)
    mock_prompt_service.custom_prompt_template.assert_awaited_once()
    mock_chain.ainvoke.assert_awaited_once_with({"input": state["input"]})
    assert result == "Test structured response"

def test_init_sets_services(mock_llm_service, mock_prompt_service):
    builder = PromptedSpreadsheetBuilder(mock_llm_service, mock_prompt_service)
    assert builder._PromptedSpreadsheetBuilder__llm_service is mock_llm_service
    assert builder._PromptedSpreadsheetBuilder__prompt_service is mock_prompt_service
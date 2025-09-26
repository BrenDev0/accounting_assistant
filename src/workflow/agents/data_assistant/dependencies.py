from fastapi import Depends

from src.workflow.services.llm_service import LlmService
from src.workflow.services.prompt_service import PromptService

from src.dependencies.services import get_llm_service, get_prompt_service, get_websocket_service

from src.api.modules.websocket.websocket_service import WebsocketService

from src.workflow.agents.data_assistant.agent import DataAssistant

def get_data_assistant(
    llm_service: LlmService = Depends(get_llm_service),
    prompt_service: PromptService = Depends(get_prompt_service),
    websocket_service: WebsocketService = Depends(get_websocket_service)
) -> DataAssistant:
    return DataAssistant(
        llm_service=llm_service,
        prompt_service=prompt_service,
        websocket_service=websocket_service
    )
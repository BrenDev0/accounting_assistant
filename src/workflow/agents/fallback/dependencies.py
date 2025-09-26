from fastapi import Depends

from src.workflow.services.llm_service import LlmService
from src.workflow.services.prompt_service import PromptService

from src.dependencies.services import get_llm_service, get_prompt_service, get_websocket_service

from src.api.modules.websocket.websocket_service import WebsocketService

from src.workflow.agents.fallback.agent import FallBackAgent

def get_fallback_agent(
    llm_service: LlmService = Depends(get_llm_service),
    prompt_service: PromptService = Depends(get_prompt_service),
    websocket_service: WebsocketService = Depends(get_websocket_service)
) -> FallBackAgent: 
    return FallBackAgent(
        llm_service=llm_service,
        prompt_service=prompt_service,
        websocket_service=websocket_service
    )
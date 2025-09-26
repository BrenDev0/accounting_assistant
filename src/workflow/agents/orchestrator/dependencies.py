from fastapi import Depends

from src.workflow.services.llm_service import LlmService
from src.workflow.services.prompt_service import PromptService

from src.dependencies.services import get_llm_service, get_prompt_service

from src.workflow.agents.orchestrator.agent import Orchestrator


def get_orchestrator(
    llm_service: LlmService = Depends(get_llm_service),
    prompt_service: PromptService = Depends(get_prompt_service)
) -> Orchestrator:
    return Orchestrator(
        llm_service=llm_service,
        prompt_service=prompt_service
    )
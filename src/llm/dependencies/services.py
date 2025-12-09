import logging
from expertise_chats.dependencies.container import Container
from expertise_chats.exceptions.dependencies import DependencyNotRegistered

from expertise_chats.llm import EmbeddingServiceAbstract, EmbeddingService, LlmServiceAbstract, LlmService, PromptService, WorkflowServiceAbsract
from src.llm.infrastructure.langgraph.workflow_service import LanggraphWorkflowService

logger = logging.getLogger(__name__)

def get_llm_service() -> LlmServiceAbstract:
    try:
        instance_key = "llm_service"
        service = Container.resolve(instance_key)

    except DependencyNotRegistered:
        service = LlmService()
        Container.register(instance_key, service)
        logger.info(f"{instance_key} registered")

    return service


def get_ebedding_service() -> EmbeddingServiceAbstract:
    try:
        instance_key = "embedding_service"
        service = Container.resolve(instance_key)

    except DependencyNotRegistered:
        service = EmbeddingService()
        Container.register(instance_key, service)
        logger.info(f"{instance_key} registered")
    
    return service

def get_prompt_service() -> PromptService:
    try:
        instance_key = "prompt_service"
        service = Container.resolve(instance_key)
    
    except DependencyNotRegistered:
        service = PromptService()

        Container.register(instance_key, service)
        logger.info(f"{instance_key} registered")
    
    return service

def get_workflow_service() -> WorkflowServiceAbsract:
    try:
        instance_key = "workflow_service"
        service = Container.resolve(instance_key)
    
    except DependencyNotRegistered:
        from  src.llm.dependencies.agents import get_orchestrator_agent, get_data_agent, get_fallback_agent, get_accounting_agent
        service = LanggraphWorkflowService(
            orchestrator=get_orchestrator_agent(),
            data_assistant=get_data_agent(),
            accounting_assistgant=get_accounting_agent(),
            fallback_agent=get_fallback_agent()
        )

        Container.register(instance_key, service)
        logger.info(f"{instance_key} registered")
    
    return service


from src.dependencies.container import Container

from src.workflow.services.embedding_service import EmbeddingService
from src.workflow.services.llm_service import LlmService
from src.workflow.services.prompt_service import PromptService
from src.workflow.agents.accounting_assistant.accounting_assistant import AccountingAssistant
from src.workflow.agents.data_assistant.data_assistant import DataAssistant
from src.workflow.agents.orchestrator.orchestrator import Orchestrator

from src.api.core.services.redis_service import RedisService
from src.api.modules.interactions.interactions_dependencies import configure_interactions_dependencies

def configure_container():
    ## Independent
    embedding_service = EmbeddingService()
    Container.register("embedding_service", embedding_service)

    llm_service = LlmService()
    Container.register("llm_service", llm_service)

    redis_service = RedisService()
    Container.register("redis_service", redis_service)


    ## Dependent
    prompt_service = PromptService(
        embedding_service=embedding_service,
        redis_service=redis_service
    )
    Container.register("prompt_service", prompt_service)

    orchestrator = Orchestrator(
        prompt_service=prompt_service,
        llm_service=llm_service
    )
    Container.register("orchestrator", orchestrator)

    accounting_assistant = AccountingAssistant(
        prompt_service=prompt_service,
        llm_service=llm_service
    )
    Container.register("accounting_assistant", accounting_assistant)

    data_assistant = DataAssistant(
        prompt_service=prompt_service,
        llm_service=llm_service
    )
    Container.register("data_assistant", data_assistant)

    ## Module

    configure_interactions_dependencies()





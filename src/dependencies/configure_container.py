from src.dependencies.container import Container

from src.workflow.services.embedding_service import EmbeddingService
from src.workflow.services.llm_service import LlmService
from src.workflow.services.prompt_service import PromptService

from src.api.core.services.redis_service import RedisService

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


    ## Module

    





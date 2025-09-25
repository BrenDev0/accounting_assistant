from fastapi import Depends

from src.workflow.services.embedding_service import EmbeddingService
from src.workflow.services.llm_service import LlmService
from src.workflow.services.prompt_service import PromptService

from src.api.core.services.redis_service import RedisService
from src.api.modules.websocket.websocket_service import WebsocketService

from src.dependencies.container import Container

def get_embeddings_service() -> EmbeddingService:
    return EmbeddingService()

def get_llm_service() -> LlmService:
    return LlmService()

def get_prompt_service(
    embedding_service: EmbeddingService = Depends(get_embeddings_service)
) -> PromptService:
    return PromptService(
        embedding_service=embedding_service
    )

def get_redis_service() -> RedisService:
    return RedisService()

def get_websocket_service() -> WebsocketService:
    return Container.resolve("websocket_service")
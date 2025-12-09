import logging
from expertise_chats.dependencies.container import Container
from expertise_chats.exceptions.dependencies import DependencyNotRegistered
from expertise_chats.llm import VectorRepositoryAbstract, VectorRepository

logger = logging.getLogger(__name__)


def get_vector_repository() -> VectorRepositoryAbstract:
    try:
        instance_key = "vector_repository"
        repository = Container.resolve(instance_key)

    except DependencyNotRegistered:
        repository = VectorRepository()
        Container.register(instance_key, repository)
        logger.info(f"{instance_key} registered")
    
    return repository
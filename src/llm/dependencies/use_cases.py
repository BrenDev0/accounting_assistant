import logging
from expertise_chats.dependencies.container import Container
from expertise_chats.exceptions.dependencies import DependencyNotRegistered
from expertise_chats.llm import SearchForContext, HandleChunk, EndAudioStream, StreamLlmOutput

from src.llm.dependencies.services import get_ebedding_service, get_llm_service
from src.llm.dependencies.repositories import get_vector_repository
from src.llm.dependencies.producers import get_producer



logger = logging.getLogger(__name__)

def get_search_for_context_use_case() -> SearchForContext:
    try:
        instance_key = "search_for_context_use_case"
        use_case = Container.resolve(instance_key)

    except DependencyNotRegistered:
        use_case = SearchForContext(
            embedding_service=get_ebedding_service(),
            vector_repository=get_vector_repository()
        )

        Container.register(instance_key, use_case)
        logger.info(f"{instance_key} registered")

    return use_case

def get_hanlde_chunk_use_case() -> HandleChunk:
    try:
        instance_key = "hanlde_chunk_use_case"
        use_case = Container.resolve(instance_key)

    except DependencyNotRegistered:
        use_case = HandleChunk(
            producer=get_producer()
        )

        Container.register(instance_key, use_case)
        logger.info(f"{instance_key} registered")

    return use_case

def get_end_audio_stream_use_case() -> EndAudioStream:
    try:
        instance_key = "end_audio_stream_use_case"
        use_case = Container.resolve(instance_key)

    except DependencyNotRegistered:
        use_case = EndAudioStream(
            producer=get_producer()
        )

        Container.register(instance_key, use_case)
        logger.info(f"{instance_key} registered")

    return use_case

def get_stream_llm_output_use_case() -> StreamLlmOutput:
    try:
        instance_key = "stream_llm_output_use_case"
        use_case = Container.resolve(instance_key)

    except DependencyNotRegistered:
        use_case = StreamLlmOutput(
            llm_service=get_llm_service(),
            chunk_hander=get_hanlde_chunk_use_case(),
            end_audio_stream=get_end_audio_stream_use_case()
        )

        Container.register(instance_key, use_case)
        logger.info(f"{instance_key} registered")

    return use_case
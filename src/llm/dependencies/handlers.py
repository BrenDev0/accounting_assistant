import logging
from expertise_chats.dependencies.container import Container
from expertise_chats.exceptions.dependencies import DependencyNotRegistered
from src.llm.events.handlers.incomming_message import IncommingMessageHandler
from src.llm.dependencies.services import get_workflow_service
from src.llm.dependencies.producers import get_producer


logger = logging.getLogger(__name__)

def get_incomming_message_handler() -> IncommingMessageHandler:
    try:
        instance_key = "incomming_message_handler"
        handler = Container.resolve(instance_key)
    
    except DependencyNotRegistered:
        handler = IncommingMessageHandler(
            workflow_service=get_workflow_service(),
            producer=get_producer()
        )
        Container.register(instance_key, handler)
        logger.info(f"{instance_key} registered")

    return handler

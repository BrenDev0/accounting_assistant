import logging
import os
from expertise_chats.dependencies.container import Container
from expertise_chats.exceptions.dependencies import DependencyNotRegistered

from expertise_chats.broker import Producer
logger = logging.getLogger(__name__)

def get_producer() -> Producer:
    try: 
        instance_key = "base_producer"
        producer = Container.resolve(instance_key)

    except DependencyNotRegistered:
        exchange = os.getenv("EXCHANGE")
        if not exchange:
            raise ValueError("Broker exchange variables not configured")
        producer = Producer(
            exchange=exchange
        )

        Container.register(instance_key, producer)
        logger.info(f"{instance_key} registered")

    return producer
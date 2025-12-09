import os
import threading
import logging
from expertise_chats.broker import Consumer, BrokerConnection

from src.llm.dependencies.handlers import get_incomming_message_handler
logger = logging.getLogger("auth.events.setup")

LLM_QUEUES = [
    ("accounting_assistant.incomming", "99b5792d-c38a-4e49-9207-a3fa547905ae.process")
]

def __setup_llm_incomming_consumer():
    consumer = Consumer(
        queue_name="accounting_assistant.incomming",
        handler=get_incomming_message_handler()
    )
    
    thread = threading.Thread(target=consumer.start, daemon=False)
    thread.start()
    logger.info("Accounting assistant inbound consumer listening")


def __initialize_llm_queues():
    EXCHANGE = os.getenv("EXCHANGE")
    channel = BrokerConnection.get_channel()

    channel.exchange_declare(
        exchange=EXCHANGE,
        exchange_type="topic",
        durable=True
    )


    for queue_name, routing_key in LLM_QUEUES:
        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_bind(
            exchange=EXCHANGE,
            queue=queue_name,
            routing_key=routing_key
        )

    logger.info("Accounting assistant queue initialized")

    __setup_llm_incomming_consumer()


def initialize_llm_broker():
    __initialize_llm_queues()
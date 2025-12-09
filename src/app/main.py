import logging
import os
from dotenv import load_dotenv
load_dotenv()
import time
from src.llm.events.setup import initialize_llm_broker

def main():
    level = os.getenv("LOGGER_LEVEL", logging.INFO)
  
    logging.basicConfig(
        level=int(level),
        format="%(levelname)s - %(name)s - %(message)s"
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("pika").setLevel(logging.WARNING)
    logging.getLogger("langsmith.client").setLevel(logging.WARNING)
    logging.getLogger("openai._base_client").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.debug("!!!!! LOGGER LEVEL SET TO DEBUG !!!!!")

    initialize_llm_broker()
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)  # Sleep to prevent busy-waiting
    except KeyboardInterrupt:
        print("Shutting down gracefully...")

if __name__ == "__main__":
    main()
import logging
from typing import Any, Dict
from expertise_chats.broker import AsyncEventHandlerBase, InteractionEvent, Producer
from expertise_chats.llm import WorkflowServiceAbsract
from expertise_chats.errors.error_handler import handle_error
from src.llm.domain.models.state import State


logger = logging.getLogger(__name__)

class IncommingMessageHandler(AsyncEventHandlerBase):
    def __init__(
        self,
        workflow_service: WorkflowServiceAbsract,
        producer: Producer
    ):
        self.__workflow_service = workflow_service
        self.__producer = producer

    async def handle(self, payload: Dict[str, Any]):
        logger.debug(f"legal assistant history handler received request ::: {payload}")

        try:
            event = InteractionEvent(**payload)
            
            state = State(
                context_orchestrator_response=None,
                general_legal_response="",
                company_legal_response="",
                final_response="",
                event=event
            )

            
            final_state: State = await self.__workflow_service.invoke_workflow(
                state=state
            )

            event.event_data = {
                    "llm_response": final_state["final_response"]
                }
            
            logger.debug(f"Publishing to messages.outgoing.send")
            self.__producer.publish(
                routing_key="messages.outgoing.send",
                event_message=event
            )
        except Exception as e: 
            logger.error(str(e))
            handle_error(
                event=event,
                producer=self.__producer,
                server_error=True
            )

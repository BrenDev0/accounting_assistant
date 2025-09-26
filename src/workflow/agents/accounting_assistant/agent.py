from fastapi import WebSocket, WebSocketDisconnect

from src.workflow.services.llm_service import LlmService
from src.workflow.services.prompt_service import PromptService
from src.workflow.state import State

from src.api.modules.websocket.websocket_service import WebsocketService

from src.utils.decorators.error_handler import error_handler

class AccountingAssistant:
    __MODULE ="accounting_assistant.agent"
    def __init__(
        self, 
        llm_service: LlmService, 
        prompt_service: PromptService,
        websocket_service: WebsocketService
    ):
        self.__llm_service = llm_service
        self.__prompt_service = prompt_service
        self.__websocket_service = websocket_service

    @error_handler(module=__MODULE)
    async def __get_prompt_template(
        self,
        state: State
    ):
        system_message = """
        You are an expert accounting assistant. 
        Answer all questions accurately and clearly, 
        providing guidance on accounting principles, 
        best practices, and financial data organization.

        - **Format your response using valid Markdown. Use headings, bullet points, numbers, indentations, and bold or italics for clarity.**
        """

        prompt = await  self.__prompt_service.custom_prompt_template(
            state=state,
            system_message=system_message,
            with_chat_history=True
        )

        return prompt

    @error_handler(module=__MODULE)
    async def interact(
        self,
        state: State
    ):
        llm = self.__llm_service.get_llm(
            temperature=0.5,
            max_tokens=250
        )

        prompt = await self.__get_prompt_template(state=state)

        chain = prompt | llm

        chunks = []
        websocket: WebSocket = self.__websocket_service.get_connection(state["chat_id"])
        try:
            async for chunk in chain.astream({"input": state["input"]}):
                if websocket:
                    try:
                        await websocket.send_json(chunk.content)
                    except WebSocketDisconnect:
                        self.__websocket_service.remove_connection(state["chat_id"])
                        websocket = None
                        raise
                chunks.append(chunk.content)
        except Exception as e:
            print(f"Error during streaming: {e}")
            raise
        
        finally:
            return "".join(chunks)

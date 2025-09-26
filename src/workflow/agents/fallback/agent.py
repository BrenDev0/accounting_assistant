from fastapi import WebSocket, WebSocketDisconnect

from src.workflow.services.prompt_service import PromptService
from src.workflow.services.llm_service import LlmService
from src.api.modules.websocket.websocket_service import WebsocketService
from src.workflow.state import State
from src.utils.decorators.error_handler import error_handler

class FallBackAgent:
    __MODULE = "fallback.agent"
    def __init__(
        self, 
        prompt_service: PromptService, 
        llm_service: LlmService,
        websocket_service: WebsocketService
    ):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service
        self.__websocket_service = websocket_service

    @error_handler(module=__MODULE)
    async def __get_prompt_template(
        self,
        state: State
    ):
        system_message = """
        You are an accounting assistant fallback agent.

        The user's request has already been determined to be outside the scope of accounting, or is too vague to answer.

        Politely inform the user that you cannot assist with their request because it is outside the scope of this assistant.

        Clearly explain that your expertise is limited to accounting topics, including:
        - General accounting principles and practices
        - Company-specific accounting data
        - Data visualizations related to company accounting records

        If the user would like help with an accounting-related question, encourage them to ask about those topics.
        - **Format your response using valid Markdown. Use headings, bullet points, numbers, indentations, and bold or italics for clarity.**
        """

        prompt = await self.__prompt_service.custom_prompt_template(
            state=state,
            system_message=system_message
        )

        return prompt

    @error_handler(module=__MODULE)
    async def interact(
        self,
        state: State
    ): 
        prompt = await self.__get_prompt_template(state=state)

        llm = self.__llm_service.get_llm(
            temperature=0.1,
            max_tokens=100
        )


        chain = prompt | llm

        chunks = []
        websokcet: WebSocket = self.__websocket_service.get_connection(state["chat_id"])

        try:
            async for chunk in chain.astream({"input": state["input"]}):
                if websokcet:
                    try:
                        await websokcet.send_json(chunk.content)
                    except WebSocketDisconnect:
                        self.__websocket_service.remove_connection(state["chat_id"])
                        websokcet = None
                chunks.append(chunk.content)
        except Exception as e:
            print(f"Error during streaming: {e}")
            raise

        finally:
            return "".join(chunks)
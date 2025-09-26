from src.workflow.services.prompt_service import PromptService
from src.workflow.services.llm_service import LlmService
from src.workflow.state import State
from src.utils.decorators.error_handler import error_handler

class FallBackAgent:
    __MODULE = "fallback.agent"
    def __init__(self, prompt_service: PromptService, llm_service: LlmService):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service

    @error_handler(module=__MODULE)
    async def __get_prompt_template(
        self,
        state: State
    ):
        system_message = """
        
        """

        prompt = await self.__prompt_service.custom_prompt_template(
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
        prompt = await self.__get_prompt_template(state=state)

        llm = self.__llm_service.get_llm(
            temperature=0.1,
            max_tokens=100
        )


        chain = prompt | llm

        response = await chain.ainvoke({"input": state["input"]})

        return response
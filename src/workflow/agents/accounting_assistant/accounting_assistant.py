from src.workflow.services.llm_service import LlmService
from src.workflow.services.prompt_service import PromptService
from src.workflow.state import State

class AccountingAssistant:
    def __init__(self, llm_service: LlmService, prompt_service: PromptService):
        self.__llm_service = llm_service
        self.__prompt_service = prompt_service

    async def __get_prompt_template(
        self,
        state: State
    ):
        system_message = """
        You are an expert accounting assistant. 
        Answer all questions accurately and clearly, 
        providing guidance on accounting principles, 
        best practices, and financial data organization.
        """

        prompt = await  self.__prompt_service.custom_prompt_template(
            state=state,
            system_message=system_message,
            with_chat_history=True,
            with_context=True,
            context_collection=f"user_{state['user_id']}_company_{state['company_id']}"
        )

        return prompt

    async def interact(
        self,
        state: State
    ):
        llm = self.__llm_service.get_llm(
            temperature=0.2,
            max_tokens=250
        )

        prompt = await self.__get_prompt_template(state=state)

        chain = prompt | llm

        response = await chain.ainvoke({"input": state['input']})

        return response.content.strip()
from src.workflow.services.llm_service import LlmService
from src.workflow.services.prompt_service import PromptService
from  src.workflow.state import State

class PromptedSpreadsheetBuilder:
    def  __init__(self, llm_service: LlmService, prompt_service: PromptService):
        self.__llm_service = llm_service
        self.__prompt_service = prompt_service

    async def __get_prompt_template(
        self,
        state: State
    ):
        system_message = """
        You are an expert accounting assistant specialized in generating structured data for spreadsheets.  
        When given a user request, extract all relevant information and return it as a list of key-value pairs, 
        where each key is a column name and each value is the corresponding cell value.  
        Use the provided context from company documents to ensure accuracy.  
        Respond only with structured data in the specified format, suitable for direct conversion to a DataFrame.
        """

        prompt = await self.__prompt_service.custom_prompt_template(
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
            max_tokens=350
        )

        prompt = await self.__get_prompt_template(state=state)

        chain = prompt | llm

        response = await chain.ainvoke({"input": state['input']})

        return response.content.strip()
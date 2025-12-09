from typing import List
from expertise_chats.llm import LlmMessageEvent, LlmServiceAbstract, PromptService, MessageModel
from src.llm.domain.models.state import State
from src.llm.domain.models.orchestrator import OrchestratorResponse

class Orchestrator:
    def __init__(self, prompt_service: PromptService, llm_service: LlmServiceAbstract):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service

    def __get_prompt(
        self,
        input: str,
        chat_history: List[MessageModel]
    ):
        system_message = """
        You are an accounting context orchestrator agent. Analyze the user's query and determine which types of information are required.

        Set the following fields to true or false:

        - general_accounting: true if the query is about general accounting principles, definitions, or practices.
        - document_specific_data: true if the query requires extracting or referencing data from specific company documents or tables.
        - data_visualization: true if the user is requesting to see, show, or display any data, table, spreadsheet, chart, or graph that is based on company documents or tables, or wants to aggregate company data into a new sheet.
        IMPORTANT: data_visualization can only be true if document_specific_data is also true. If the user asks to see, show, or list general accounting facts or principles (not company data), data_visualization must be false.

        If the user's request is too vague to determine, or is outside the scope of accounting, set all fields to false.

        Multiple fields can be true simultaneously.

        Respond ONLY in the following JSON format:
        {
            "general_accounting": true or false,
            "document_specific_data": true or false,
            "data_visualization": true or false
        }
        Examples:

        User: What is double-entry bookkeeping?
        Response:
        {
            "general_accounting": true,
            "document_specific_data": false,
            "data_visualization": false
        }

        User: Show me monthly revenue from our invoices.
        Response:
        {
            "general_accounting": false,
            "document_specific_data": true,
            "data_visualization": true
        }

        User: What are our total expenses for the year so far.
        Response:
        {
            "general_accounting": false,
            "document_specific_data": true,
            "data_visualization": false
        }

        User: Show me the top ten accounting principles and their inception dates.
        Response:
        {
            "general_accounting": true,
            "document_specific_data": false,
            "data_visualization": false
        }

        User: Can you help me with something?
        Response:
        {
            "general_accounting": false,
            "document_specific_data": false,
            "data_visualization": false
        }

        User: Tell me about the weather in Paris.
        Response:
        {
            "general_accounting": false,
            "document_specific_data": false,
            "data_visualization": false
        }
        """

        prompt = self.__prompt_service.build_prompt(
            system_message=system_message,
            input=input,
            chat_history=chat_history
        )

        return prompt

    async def interact(
        self,
        state: State
    ): 
        try:
            event = state["event"]        
            event_data = LlmMessageEvent(**event.event_data)

            prompt = self.__get_prompt(
                input=event_data.chat_history[0].text,
                chat_history=event_data.chat_history
            )


            response = await self.__llm_service.invoke_structured(
                prompt=prompt,
                response_model=OrchestratorResponse,
                temperature=0.5
            )

            return response

        except Exception:
            raise
from src.workflow.services.prompt_service import PromptService
from src.workflow.services.llm_service import LlmService
from src.workflow.state import State
from src.workflow.agents.orchestrator.models import OrchestratorResponse
from src.utils.decorators.error_handler import error_handler

class Orchestrator:
    __MODULE = "orchestrator.agent"
    def __init__(self, prompt_service: PromptService, llm_service: LlmService):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service

    @error_handler(module=__MODULE)
    async def __get_prompt_template(
        self,
        state: State
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

        structured_llm = llm.with_structured_output(OrchestratorResponse)

        chain = prompt | structured_llm

        response = await chain.ainvoke({"input": state["input"]})

        return response
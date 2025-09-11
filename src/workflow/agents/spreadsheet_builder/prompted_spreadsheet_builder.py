from src.workflow.services.llm_service import LlmService
from src.workflow.services.prompt_service import PromptService
from  src.workflow.state import State

class PromptedSpreadsheetBuilder:
    def  __init__(self, llm_service: LlmService, prompt_service: PromptService):
        self.__llm_service = llm_service
        self.__prompt_service = prompt_service

    def __get_prompt_template(
        self,
        state: State
    ):
        pass

    async def interact(
        self,
        state: State
    ):
        pass
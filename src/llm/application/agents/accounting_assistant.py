from  typing import List
from expertise_chats.llm import PromptService, StreamLlmOutput, MessageModel, LlmMessageEvent
from src.llm.domain.models.state import State


class AccountingAssistant:
    def __init__(
        self, 
        stream_llm_output: StreamLlmOutput,
        prompt_service: PromptService
    ):
        self.__stream_llm_output = stream_llm_output
        self.__prompt_service = prompt_service
        

    def __get_prompt(
        self,
        input: str,
        chat_history: List[MessageModel]
    ):
        system_message = """
        You are an expert accounting assistant. 
        Answer all questions accurately and clearly, 
        providing guidance on accounting principles, 
        best practices, and financial data organization.

        - **Format your response using valid Markdown. Use headings, bullet points, numbers, indentations, and bold or italics for clarity.**
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

            response = await self.__stream_llm_output.execute(
                prompt=prompt,
                event=event.model_copy(),
                temperature=0.5
            )

            return response
            
        except Exception:
           
            raise
        
     

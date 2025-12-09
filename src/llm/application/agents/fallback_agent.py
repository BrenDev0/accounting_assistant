from expertise_chats.llm import PromptService, StreamLlmOutput, LlmMessageEvent
from src.llm.domain.models.state import State


class FallBackAgent:
    def __init__(
        self, 
        prompt_service: PromptService, 
        stream_llm_output: StreamLlmOutput
    ):
        self.__prompt_service = prompt_service
        self.__stream_llm_output = stream_llm_output

    async def __get_prompt(
        self,
        input: str
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

        prompt = await self.__prompt_service.build_prompt(
            system_message=system_message,
            input=input
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
                input=event_data.chat_history[0].text
            )

            response = await self.__stream_llm_output.execute(
                prompt=prompt,
                event=event.model_copy(),
                temperature=0.5
            )

            return response
        except Exception:
            raise
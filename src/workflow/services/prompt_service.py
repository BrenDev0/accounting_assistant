from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from typing import List, Dict, Any
from src.api.core.services.redis_service import RedisService
from src.workflow.services.embedding_service import EmbeddingService
from src.workflow.state import State

class PromptService:
    def __init__(self, embedding_service: EmbeddingService, redis_service: RedisService):
        self.embedding_service = embedding_service
        self.redis_service = redis_service


    async def custom_prompt_template(
        self, 
        state: State, 
        system_message: str, 
        with_chat_history: bool = False, 
        with_context: bool = False, 
        context_collection: str = None,
        context_top_k: int = 4
    ):
        messages = [
            SystemMessagePromptTemplate.from_template(system_message)
        ]

        if with_chat_history:
            messages = self.add_chat_history(state, messages)

        if with_context and context_collection != None:
            messages = await self.add_context(
                input=state["input"], 
                messages=messages, 
                collection_name=context_collection,
                top_k=context_top_k
            )

        messages.append(HumanMessagePromptTemplate.from_template('{input}'))

        prompt = ChatPromptTemplate.from_messages(messages)

        return prompt


    async def add_context(
        self, 
        input: str, 
        messages: List[Dict[str, Any]], 
        collection_name: str,
        top_k: int = 4
    ) -> List[Any]:
        context = await self.embedding_service.search_for_context(
            query=input,
            collection_name=collection_name,
            top_k=top_k
        )
 
        if context:
            messages.append(SystemMessage(content=f"""
                You have access to the following relevant context retrieved from documents.
                Use this information to inform your response. Do not make up facts outside of this context.

                Relevant context:
                {context}
            """))

        return messages

    @staticmethod
    def add_chat_history(state: State, messages: List[Any]) -> List[Any]:

        chat_history = state.get("chat_history", [])
        if chat_history:
            for msg in chat_history:
                if msg["message_type"] == "human":
                    messages.append(HumanMessage(content=msg["text"]))
                elif msg["message_type"] == "ai":
                    messages.append(AIMessage(content=msg["text"]))

        return messages
    
    
    
    
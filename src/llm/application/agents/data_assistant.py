from langchain_community.utilities import SQLDatabase
from sqlalchemy import select, text
from src.database.database import engine
from src.llm.domain.models.state import State
from typing import List, Any, Dict
import re
from expertise_chats.llm import PromptService, LlmServiceAbstract, LlmMessageEvent, StreamLlmOutput, MessageModel
from expertise_chats.broker import Producer
from expertise_chats.schemas.ws import WsPayload

from src.database.database_models import TenantTable
from src.llm.domain.models.data_assistant import DataAssistantResponse




class DataAssistant:
    def __init__(
        self, 
        prompt_service: PromptService, 
        llm_service: LlmServiceAbstract,
        stream_llm_output: StreamLlmOutput,
        producer: Producer
    ):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service
        self.__stream_llm_output = stream_llm_output
        self.__producer = producer

    def __get_tenant_tables(
        self,
        state: State
    ) -> List[str]:
        db = state["db"]
        stmt = select(TenantTable.table_name).where(TenantTable.company_id == state["company_id"])
        result = db.execute(stmt)

        tables = [row[0] for row in result.fetchall()]
        
        return tables
    
    async def __get_sql_prompt(
        self,
        input: str,
        chat_history: List[MessageModel],
        dialect,
        table_info
    ): 
        print("TABLE INFO:::::::::::", table_info)
        system_message = f"""
        You are a read-only SQL assistant.

        Given an input question, return a syntactically correct {dialect} SELECT query using only the tables listed below.

        **IMPORTANT: Always use double quotes around column names and table names that contain special characters like spaces, parentheses, or percentage signs.**

        If you cannot find a relevant table, or if the question is too vague to answer with the available context, respond in this JSON format:
        {{
        "sql": null,
        "error": "<A clear explanation of the issue, e.g. 'No relevant table found' or 'Question is too vague to answer'>"
        }}

        If you can answer, respond in this JSON format:
        {{
        "sql": "<the SQL SELECT statement>",
        "error": null
        }}

        Only use the following tables:
        {table_info}

        Never use tables or columns not listed above.
        Never explain your answer unless returning an error.
        """

        prompt = await self.__prompt_service.build_prompt(
            system_message=system_message,
            input=input,
            chat_history=chat_history
        ) 

        return prompt
    
    async def __handle_no_visual(
        self,
        state: State,
        sql_data: List[Dict[str, Any]]
    ):
        system_prompt = f"""
        Answer the users query using the provided data
     
        the data is :
        {sql_data}

        - **Format your response using valid Markdown. Use headings, bullet points, numbers, indentations, and bold or italics for clarity.**
        """
   
        try:
            event = state["event"]        
            event_data = LlmMessageEvent(**event.event_data)

            prompt = self.__prompt_service.build_prompt(
                system_message=system_prompt,
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


    async def interact(
        self,
        state: State
    ):
        try:
            table_names = self.__get_tenant_tables(state=state)
        
            db = SQLDatabase(
                engine=engine,
                include_tables=table_names,
                sample_rows_in_table_info=2
            )

            prompt = await self.__get_sql_prompt(
                state=state,
                dialect=db.dialect,
                table_info=db.get_table_info(
                    table_names=table_names
                )
            )

            res: DataAssistantResponse = await self.__llm_service.invoke_structured(
                prompt=prompt,
                response_model=DataAssistantResponse,
                temperature=0.0
            )

            if res.sql:
                sql =  res.sql.strip()
                sql = re.sub(r"^```sql\s*|^```|```$", "", sql, flags=re.MULTILINE).strip()

                if not sql.lower().lstrip().startswith("select"):
                    raise ValueError("Invalid query.")
            
                result = state["db"].execute(text(sql))
                data_response =  [Dict(row) for row in result.mappings().all()]
            elif res.error:
                data_response = res.error

            else: 
                data_response = "Error"    
            
            if not state["orchestrator_response"].data_visualization:
                response = await self.__handle_no_visual(
                    state=state,
                    sql_data=data_response
                )

                return response

            else:
                event = state["event"]        
                event_data = LlmMessageEvent(**event.event_data)

                ws_payload = WsPayload(
                    message_id=event_data.chat_history[0].message_id,
                    type="ROWS",
                    data=data_response
                )

                event.event_data =ws_payload.model_dump()

                self.__producer.publish(
                    routing_key="streaming.general.outbound.send",
                    event_message=event
                )

                return data_response 
        
        except Exception:
            raise

            

from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from sqlalchemy import select, text
from src.database.database import engine
from src.workflow.state import State
from typing import List, Any, Dict
import re
from fastapi import WebSocket, WebSocketDisconnect

from src.database.database_models import TenantTable

from src.workflow.services.prompt_service import PromptService
from src.workflow.services.llm_service import LlmService
from src.workflow.agents.data_assistant.data_assistant_models import DataAssistantRespone

from src.utils.decorators.error_handler import  error_handler

from src.api.modules.websocket.websocket_service import WebsocketService



class DataAssistant:
    __MODULE = "data_assistant.agent"
    def __init__(
        self, 
        prompt_service: PromptService, 
        llm_service: LlmService,
        websocket_service: WebsocketService
    ):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service
        self.__websocket_service = websocket_service

    def __get_tenant_tables(
        self,
        state: State
    ) -> List[str]:
        db = state["db"]
        stmt = select(TenantTable.table_name).where(TenantTable.company_id == state["company_id"])
        result = db.execute(stmt)

        tables = [row[0] for row in result.fetchall()]
        
        return tables
    
    async def __get_prompt_template(
        self,
        state: State
    ): 
        system_message = """
        You are a read-only SQL assistant.

        Given an input question, return a syntactically correct {dialect} SELECT query using only the tables listed below.

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

        prompt = await self.__prompt_service.custom_prompt_template(
            state=state,
            system_message=system_message,
            with_chat_history=True
        ) 

        return prompt
    
    async def __handle_no_visual(
        self,
        state: State,
        sql_data: List[Dict[str, Any]],
        llm: ChatOpenAI
    ):
        system_prompt = """
        Answer the users query using the provided data
     
        the data is :
        {data}
        """
        prompt = await self.__prompt_service.custom_prompt_template(
            state=state,
            system_message=system_prompt
        )

        chain = prompt | llm

        chunks = []
        websocket: WebSocket = self.__websocket_service.get_connection(state["chat_id"])

        try:
            async for chunk in chain.astream({
                "input": state["input"],
                "data": sql_data
            }):
                if websocket:
                    try:
                        await websocket.send_json(chunk.content)
                    except WebSocketDisconnect:
                        self.__websocket_service.remove_connection(state["chat_id"])
                        websocket = None
                chunks.append(chunk.content)
        except Exception as e:
            print(f"Error during streaming: {e}")
            raise
        
        finally:
            return "".join(chunks)


    
    @error_handler(module=__MODULE)
    async def interact(
        self,
        state: State
    ):
        prompt = await self.__get_prompt_template(state=state)
        
        llm = self.__llm_service.get_llm(
            temperature=0,
            max_tokens=500
        )

        structured_llm = llm.with_structured_output(DataAssistantRespone)

        table_names = self.__get_tenant_tables(state=state)
       
        db = SQLDatabase(
            engine=engine,
            include_tables=table_names,
            sample_rows_in_table_info=2
        )

        websocket: WebSocket = self.__websocket_service.get_connection(state["chat_id"])
    
        chain = prompt | structured_llm

        res: DataAssistantRespone = await chain.ainvoke(
            {
                "dialect": db.dialect,
                "table_info": db.get_table_info(
                    table_names=table_names
                ),
                "input": state["input"]
            }
        )

        if res.sql:
            sql =  res.sql.strip()
            sql = re.sub(r"^```sql\s*|^```|```$", "", sql, flags=re.MULTILINE).strip()

            if not sql.lower().lstrip().startswith("select"):
                raise ValueError("Invalid query.")
        
            result = state["db"].execute(text(sql))
            data_response =  [dict(row) for row in result.mappings().all()]
        elif res.error:
            data_response = res.error

        else: 
            data_response = "Error"    
        
        if not state["orchestrator_response"].data_visualization:
            response = await self.__handle_no_visual(
                state=state,
                sql_data=data_response,
                llm=llm
            )

            return response

        else:
            if websocket:
                try:
                    await websocket.send_json(data_response)
                except WebSocketDisconnect:
                    self.__websocket_service.remove_connection(state["chat_id"])
                    websocket = None
                    raise
        
            return data_response 

            

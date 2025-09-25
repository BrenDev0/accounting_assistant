from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from sqlalchemy import select, text
from src.database.database import engine
from src.workflow.state import State
from typing import List, Any
import re
from fastapi import WebSocket, WebSocketDisconnect

from src.database.database_models import TenantTable

from src.workflow.services.prompt_service import PromptService
from src.workflow.services.llm_service import LlmService

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
        Given an input question, create a read only syntactically correct {dialect} query 
        to help find the answer. Never limit your query unless the user specifies in his question a
        specific number of examples they wish to obtain. 
        
        Pay attention to use only the column names that you can see in the schema
        description. Be careful to not query for columns that do not exist. Also,
        pay attention to which column is in which table.
        
        Only use the following tables:
        {table_info}

        You will not explain your answer.
        You will only return syntactically correct {dialect} query.
        Your query can only be a read only query.
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
            temperature=0,
            max_tokens=500
        )

        table_names = self.__get_tenant_tables(state=state)
       
        db = SQLDatabase(
            engine=engine,
            include_tables=table_names,
            sample_rows_in_table_info=2
        )

        toolkit = SQLDatabaseToolkit(db=db, llm=llm)

        websocket: WebSocket = self.__websocket_service.get_connection(state["chat_id"])
    
        if state["orchestrator_response"].data_visualization:

            chain = prompt | llm

            res = await chain.ainvoke(
                {
                    "dialect": db.dialect,
                    "table_info": db.get_table_info(
                        table_names=table_names
                    ),
                    "input": state["input"]
                }
            )

            sql =  res.content.strip()
            sql = re.sub(r"^```sql\s*|^```|```$", "", sql, flags=re.MULTILINE).strip()

            if not sql.lower().lstrip().startswith("select"):
                raise ValueError("Invalid query.")
            
            result = state["db"].execute(text(sql))
            final_response =  [dict(row) for row in result.mappings().all()]

            if websocket:
                try:
                    await websocket.send_json(final_response)
                except WebSocketDisconnect:
                    self.__websocket_service.remove_connection(state["chat_id"])
                    websocket = None
                    raise
            
            return final_response

            

        else: 
            agent = create_sql_agent(
                llm=llm,
                toolkit=toolkit,
                agent_type="openai-tools",
                verbose=True,
                max_iterations=10,
                early_stopping_method="force",
                top_k=100
            )

            chunks = []
            try: 
                async for chunk in agent.astream({"input": state["input"]}):
                    if websocket:
                        try: 
                            await websocket.send_json(chunk["output"])
                        except WebSocketDisconnect:
                            self.__websocket_service.remove_connection(state["chat_id"])
                            websocket = None
                            raise
                    chunks.append(chunk["output"])
            except Exception as e:
                print(f"Error during streaming: {e}")
                raise
                
            finally:
                return "".join(chunks)
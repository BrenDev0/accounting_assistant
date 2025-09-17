from src.database.database import get_db_session
from fastapi import Depends
from sqlalchemy.orm import Session
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from src.workflow.state import State
from sqlalchemy import select, create_engine, text
from src.database.database_models import TenantTable
from src.workflow.services.prompt_service import PromptService
from src.workflow.services.llm_service import LlmService
from typing import List
import os 
from src.utils.decorators.error_handler import  error_handler
import re

class DataAssistant:
    __MODULE = "data_assistant.agent"
    def __init__(self, prompt_service: PromptService, llm_service: LlmService):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service

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
        Your only job is to generate read only sql statments. 
        - Use the exact table names as provided above, including the tenant prefixes.
        - Do not shorten or modify table names.
        - Your answer will only be the raw and valid sql statement.
        - You will not explain your answer.
        - You will not reformat the answer.
        - You will not execute any query in th db.
        - You will not add a limit unless the inputs requires one.
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
            temperature=0
        )

        table_names = self.__get_tenant_tables(state=state)
        engine = create_engine(os.getenv("DATABASE_URL"))
        db = SQLDatabase(
            engine=engine,
            include_tables=table_names,
            sample_rows_in_table_info=2
        )

        toolkit = SQLDatabaseToolkit(db=db, llm=llm)

        agent = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True,
            agent_type="openai-tools",
            max_iterations=10,
            early_stopping_method="force",
            top_k=0
        )

        chain = prompt | agent

        res = await chain.ainvoke({"input": state["input"]})

        sql =  res["output"].strip()
        sql = re.sub(r"^```sql\s*|^```|```$", "", sql, flags=re.MULTILINE).strip()
        
        result = state["db"].execute(text(sql))
   
        return result.mappings().all()
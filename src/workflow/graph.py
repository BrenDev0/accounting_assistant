from fastapi import Depends
from langgraph.graph import StateGraph, END, START
import os
import httpx
from typing import List

from src.workflow.state import State
from src.workflow.agents.accounting_assistant.agent import AccountingAssistant
from src.workflow.agents.accounting_assistant.dependencies import get_accounting_assistant
from src.workflow.agents.data_assistant.agent import DataAssistant
from src.workflow.agents.data_assistant.dependencies import get_data_assistant
from src.workflow.agents.orchestrator.agent import Orchestrator
from src.workflow.agents.orchestrator.dependencies import get_orchestrator
from src.workflow.agents.orchestrator.models import OrchestratorResponse
from src.workflow.agents.fallback.agent import FallBackAgent
from src.workflow.agents.fallback.dependencies import get_fallback_agent

from src.utils.http.hmac import generate_hmac_headers


def create_graph(
    orchestrator: Orchestrator = Depends(get_orchestrator),
    accounting_assistant: AccountingAssistant = Depends(get_accounting_assistant),
    data_assistant: DataAssistant = Depends(get_data_assistant),
    fallback_agent: FallBackAgent = Depends(get_fallback_agent)
):

    graph = StateGraph(State)

    async def orchestrator_node(state: State):
        response = await orchestrator.interact(state=state)

        return {"orchestrator_response": response}
    

    async def router(state: State):
        orchestrator_response: OrchestratorResponse = state["orchestrator_response"]

        if orchestrator_response.document_specific_data:
            return "data_assistant"
        elif orchestrator_response.general_accounting:
            return "accounting_assistant"
        else:
            return "fallback"
        

    async def fallback_node(state: State):
        response = await fallback_agent.interact(state=state)
        return {"fallback": response}

    async def accounting_assistant_node(state: State):
        response = await accounting_assistant.interact(state=state)

        return {"accounting_assistant_response": response}
    
    async def data_assistant_node(state: State):
        response = await data_assistant.interact(state=state)

        return {"data_assistant_response": response}
    
    async def handle_response_node(state: State):
        hmac_headers = generate_hmac_headers(os.getenv("HMAC_SECRET"))
        main_server = os.getenv("MAIN_SERVER_ENDPOINT")
        
        if state["data_assistant_response"]:
            response = state["data_assistant_response"]

        elif state["accounting_assistant_response"]:
            response = state["accounting_assistant_response"]
        
        elif state["fallback"]:
            response = state["fallback"]
        
        else: 
            return 
        
        req_body = {
            "sender": os.getenv("AGENT_ID"),
            "message_type": "ai",
            "text": None,
            "json_data": None
        }

        if isinstance(List, response):
            req_body["json_data"] = response
        else:
            req_body["text"] = response
        
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{main_server}/messages/internal/{state['chat_id']}",
                headers=hmac_headers,
                json=req_body
            )

            return state


    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("fallback", fallback_node)
    graph.add_node("accounting_assistant", accounting_assistant_node)
    graph.add_node("data_assistant", data_assistant_node)
    graph.add_node("handle_response", handle_response_node)

    graph.add_edge(START, "orchestrator")
    graph.add_conditional_edges(
        "orchestrator",
        router,
        {
            "accounting_assistant": "accounting_assistant",
            "data_assistant": "data_assistant",
            "fallback": "fallback"
        }
    )
    graph.add_edge("accounting_assistant", "handle_response")
    graph.add_edge("data_assistant", "handle_response")
    graph.add_edge("fallback", "handle_response")
    graph.add_edge("handle_response", END)


    return graph.compile()

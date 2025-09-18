from src.workflow.state import State
from src.dependencies.container import Container
from langgraph.graph import StateGraph, END, START
from src.dependencies.container import Container
from src.workflow.agents.accounting_assistant.accounting_assistant import AccountingAssistant
from src.workflow.agents.data_assistant.data_assistant import DataAssistant
from src.workflow.agents.orchestrator.orchestrator import Orchestrator
from src.workflow.agents.orchestrator.orchestrator_models import OrchestratorResponse

def create_graph():

    graph = StateGraph(State)

    async def orchestrator_node(state: State):
        orchestrator: Orchestrator = Container.resolve("orchestrator")

        response = await orchestrator.interact(state=state)

        return {"orchestrator_response": response}
    

    async def router_node(state: State):
        orchestrator_response: OrchestratorResponse = state["orchestrator_response"]

        if orchestrator_response.document_specific_data:
            return "data_assistant"
        else:
            return "accounting_assistant"
        

    async def accounting_assistant_node(state: State):
        accounting_assistant: AccountingAssistant = Container.resolve("accounting_assistant")

        response = await accounting_assistant.interact(state=state)

        return {"accounting_assistant_response": response}
    
    async def data_assistant_node(state: State):
        data_assistant: DataAssistant = Container.resolve("data_assistant")

        response = await data_assistant.interact(state=state)

        return {"data_assistant_response": response}


    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("router", router_node)
    graph.add_node("accounting_assistant", accounting_assistant_node)
    graph.add_node("data_assistant", data_assistant_node)

    graph.add_edge(START, "orchestrator")
    graph.add_edge("orchestrator", "router")
    graph.add_edge("accounting_assistant", END)
    graph.add_edge("data_assistant", END)


    return graph.compile()

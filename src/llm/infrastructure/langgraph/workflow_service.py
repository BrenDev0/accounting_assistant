from typing import List
import logging
from langgraph.graph import START, END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from expertise_chats.llm import WorkflowServiceAbsract
from src.llm.application.agents.accounting_assistant import AccountingAssistant
from src.llm.application.agents.orchestrator import Orchestrator
from src.llm.application.agents.data_assistant import DataAssistant
from src.llm.application.agents.fallback_agent import FallBackAgent
from src.llm.domain.models.state import State
from src.llm.domain.models.orchestrator import OrchestratorResponse


logger = logging.getLogger(__name__)

class LanggraphWorkflowService(WorkflowServiceAbsract):
    def __init__(
        self,
        orchestrator: Orchestrator,
        data_assistant: DataAssistant,
        accounting_assistgant: AccountingAssistant,
        fallback_agent: FallBackAgent
    ):
       self.__orchestrator = orchestrator
       self.__data_assistant = data_assistant
       self.__accounting_assistant = accounting_assistgant
       self.__fallback_agent = fallback_agent

    def create_workflow(self):
        graph = StateGraph(State)

        async def orchestrator_node(state: State):
            response = await self.__orchestrator.interact(state=state)

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
            response = await self.__fallback_agent.interact(state=state)
            return {"fallback": response}

        async def accounting_assistant_node(state: State):
            response = await self.__accounting_assistant.interact(state=state)

            return {"accounting_assistant_response": response}
        
        async def data_assistant_node(state: State):
            response = await self.__data_assistant.interact(state=state)

            return {"data_assistant_response": response}
        
    

        graph.add_node("orchestrator", orchestrator_node)
        graph.add_node("fallback", fallback_node)
        graph.add_node("accounting_assistant", accounting_assistant_node)
        graph.add_node("data_assistant", data_assistant_node)

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
        graph.add_edge("accounting_assistant", END)
        graph.add_edge("data_assistant", END)
        graph.add_edge("fallback", END)
        


        return graph.compile()
    
    async def invoke_workflow(self, state):
        graph: CompiledStateGraph = self.create_workflow()
        try:
            final_state = await graph.ainvoke(state)
    
            return final_state
        
        except Exception:
            raise
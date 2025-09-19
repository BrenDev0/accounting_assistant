from  fastapi import Request, BackgroundTasks
from src.workflow.state import State
from src.api.modules.interactions.interactions_models import InteractionResponse

class InteractionsController: 
    async def interact(
        backgound_tasks: BackgroundTasks,
        req: Request,
        state: State,
        graph,
    ) -> InteractionResponse:
        final_state: State = await graph.ainvoke(state)
        if final_state["accounting_assistant_response"]:
            response = final_state["accounting_assistant_response"]
        else:
            response = final_state["data_assistant_response"]
        return InteractionResponse(
            response=response
        )
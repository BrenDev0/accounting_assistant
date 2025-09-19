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

        return InteractionResponse(
            response=final_state["final_response"]
        )
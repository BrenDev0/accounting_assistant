from  fastapi import Request, BackgroundTasks
from src.workflow.state import State
from src.api.core.models.http_respones import CommonHttpResponse

class InteractionsController: 
    async def interact(
        backgound_tasks: BackgroundTasks,
        req: Request,
        state: State,
        graph,
    ) -> CommonHttpResponse:
        backgound_tasks.add_task(graph.ainvoke, state)
        
        return CommonHttpResponse(
            detail="Request received"
        )
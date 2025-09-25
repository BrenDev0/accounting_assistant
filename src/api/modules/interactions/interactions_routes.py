from fastapi import APIRouter, Body, Request, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from src.api.modules.interactions.interactions_models import InteractionRequest, InteractionResponse
from src.api.modules.interactions.interactions_controller import InteractionsController
from src.api.modules.interactions.interactions_dependencies import get_interactions_controller

from src.api.core.middleware.hmac_verification import verify_hmac
from src.api.core.models.http_respones import CommonHttpResponse

from src.workflow.state import State
from src.workflow.graph import create_graph

from src.database.database import get_db_session

router = APIRouter(
    prefix="/interactions",
    tags=["Interactions"]
)

async def get_state(data: InteractionRequest = Body(...), db: Session = Depends(get_db_session)):
    state = State(
        user_id=data.user_id,
        company_id=data.company_id,
        chat_id=data.chat_id,
        chat_history=data.chat_history,
        input=data.input,
        db=db,
        orchestrator_response=None,
        accounting_assistant_response=None,
        data_assistant_response=None
    )

    return state

@router.post("/internal/interact", status_code=202, response_model=CommonHttpResponse)
async def secure_interact(
    background_tasks: BackgroundTasks,
    req: Request,
    _: None = Depends(verify_hmac),
    state: State = Depends(get_state),
    graph = Depends(create_graph),
    controller: InteractionsController = Depends(get_interactions_controller)
):
    return await controller.interact(
        background_tasks=background_tasks,
        req=req,
        state=state,
        graph=graph
    )
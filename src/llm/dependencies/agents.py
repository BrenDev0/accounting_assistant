import logging
from expertise_chats.dependencies.container import Container
from expertise_chats.exceptions.dependencies import DependencyNotRegistered

from src.llm.application.agents.accounting_assistant import AccountingAssistant
from src.llm.application.agents.orchestrator import Orchestrator
from src.llm.application.agents.data_assistant import DataAssistant
from src.llm.application.agents.fallback_agent import FallBackAgent


from src.llm.dependencies.services import  get_llm_service, get_prompt_service
from src.llm.dependencies.use_cases import get_search_for_context_use_case, get_stream_llm_output_use_case
from src.llm.dependencies.producers import get_producer

logger = logging.getLogger(__name__)

def get_orchestrator_agent() -> Orchestrator:
    try: 
        instance_key = "orchestrator_agent"
        agent = Container.resolve(instance_key)
    
    except DependencyNotRegistered:
        agent = Orchestrator(
            prompt_service=get_prompt_service(),
            llm_service=get_llm_service()
        )

        Container.register(instance_key, agent)
        logger.info(f"{instance_key} registered")
    
    return agent


def get_accounting_agent() -> AccountingAssistant:
    try: 
        instance_key = "accounting_agent"
        agent = Container.resolve(instance_key)
    
    except DependencyNotRegistered:
        agent = AccountingAssistant(
            prompt_service=get_prompt_service(),
            stream_llm_output=get_stream_llm_output_use_case()
        )

        Container.register(instance_key, agent)
        logger.info(f"{instance_key} registered")
    
    return agent

def get_data_agent() -> DataAssistant:
    try: 
        instance_key = "data_agent"
        agent = Container.resolve(instance_key)
    
    except DependencyNotRegistered:
        agent = DataAssistant(
            prompt_service=get_prompt_service(),
            llm_service=get_llm_service(),
            stream_llm_output=get_stream_llm_output_use_case(),
            producer=get_producer()
        )

        Container.register(instance_key, agent)
        logger.info(f"{instance_key} registered")
    
    return agent



def get_fallback_agent() -> FallBackAgent:
    try: 
        instance_key = "fallback_agent"
        agent = Container.resolve(instance_key)
    
    except DependencyNotRegistered:
        agent = FallBackAgent(
            prompt_service=get_prompt_service(),
            stream_llm_output=get_stream_llm_output_use_case()
        )

        Container.register(instance_key, agent)
        logger.info(f"{instance_key} registered")
    
    return agent




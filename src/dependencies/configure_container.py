from src.dependencies.container import Container

from src.utils.logs.logger import Logger

from src.api.modules.websocket.websocket_dependencies import configure_websocket_dependencies

def configure_container():
    """
    Configure non request scoped dependencies here
    """
    logger = Logger()
    Container.register("logger", logger)

    ## modules
    configure_websocket_dependencies()
   
from src.api.modules.websocket.websocket_service import WebsocketService
from src.dependencies.container import Container

def configure_websocket_dependencies(): 
    service = WebsocketService()
    Container.register("websocket_service", service)
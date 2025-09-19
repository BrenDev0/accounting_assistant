from src.api.modules.interactions.interactions_controller import InteractionsController
from src.dependencies.container import Container


def configure_interactions_dependencies():
    controller = InteractionsController()

    Container.register("interactions_controller", controller)
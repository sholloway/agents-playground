from agents_playground.simulation.context import SimulationContext
from agents_playground.sys.logger import get_default_logger

logger = get_default_logger()

def render_entities(**data) -> None:
    logger.info("Renderer: render_entities")
    context: SimulationContext = data["context"]

    # Entities is a types.SimpleNamespace with each attribute
    # on entities being a list. If we assume that the order of groupings doesn't
    # matter, then we could potential have a nested for loop.
    # Something like this...
    for _, entity_grouping in context.scene.entities.items():
        for _, entity in entity_grouping.items():
            entity.render(context)

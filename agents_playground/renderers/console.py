import dearpygui.dearpygui as dpg
from agents_playground.core.constants import DEFAULT_FONT_SIZE
from agents_playground.renderers.color import Colors
from agents_playground.simulation.context import SimulationContext

from agents_playground.sys.logger import get_default_logger

logger = get_default_logger()


def render_console(**data) -> None:
    logger.info("Renderer: render_console")
    context: SimulationContext = data["context"]
    dpg.draw_rectangle(
        pmin=(0, 0),
        pmax=(context.canvas.width, context.canvas.height),
        fill=(30, 30, 30),
    )
    dpg.draw_text(
        tag=context.console.input_widget,
        pos=(10, 10),
        text=chr(0xE285),
        color=Colors.green.value,
        size=DEFAULT_FONT_SIZE,
    )

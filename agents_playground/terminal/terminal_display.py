import dearpygui.dearpygui as dpg

from agents_playground.core.constants import DEFAULT_FONT_SIZE
from agents_playground.renderers.color import Colors
from agents_playground.simulation.context import SimulationContext
from agents_playground.simulation.tag import Tag
from agents_playground.terminal.terminal_buffer import TerminalBuffer, TerminalBufferContent

TERM_DISPLAY_INITIAL_TOP_OFFSET = 10
TERM_DISPLAY_LEFT_OFFSET = 10
TERM_DISPLAY_LINE_HEIGHT = DEFAULT_FONT_SIZE
TERM_FONT_ADVANCE = 7.2 # The width of a text glyph.
TERM_DISPLAY_VERTICAL_LINE_SPACE = 4
TERM_DISPLAY_HORIZONTAL_LINE_SPACE = 10
TERM_PROMPT_CHAR = chr(0x2588)
TERM_ACTIVE_PROMPT_INDICATOR = chr(0xE285)

class TerminalDisplay:
  def __init__(
    self, 
    terminal_layer_id: Tag, 
    display_id: Tag, 
    context: SimulationContext
  ) -> None:
    self._terminal_layer_id = terminal_layer_id
    self._display_id        = display_id
    self._context           = context

  def refresh(self, screen_buffer: TerminalBuffer) -> None:
    """
    Because I want to use a rolling screen buffer for the output and I want to 
    colorize text, I can't use a single draw_text command that I update.
    I need a way to add draw_text commands in a loop.

    On container's Slot 2 is used for draw items.
    I think a refresh could ideally be to:
    1. Clear Slot 2 on the terminal draw_layer.
    2. Add loop through the deque scroll_back_buffer and add a draw_text for each
       item. I can add to a layer by setting the layer as the parent on the draw_text.
    3. Draw the active command prompt. There is probably an optimization I could 
       do to not do steps 1 - 2 when typing.   
    """
    # Clear all drawable Items
    dpg.delete_item(
      item = self._terminal_layer_id, 
      children_only=True, 
      slot = 2
    )

    # Draw the background
    dpg.draw_rectangle(
      parent = self._terminal_layer_id,
      pmin = (0, 0),
      pmax = (self._context.canvas.width, self._context.canvas.height),
      fill = (30, 30, 30)
    )

    # Draw the Output Buffer if any.
    current_line: int = 0
    vertical_offset: int = 0
    buffer_line: TerminalBufferContent
    for buffer_line in screen_buffer.scroll_back_buffer:
      vertical_offset = TERM_DISPLAY_INITIAL_TOP_OFFSET + \
        (current_line * TERM_DISPLAY_LINE_HEIGHT) + \
        (current_line * TERM_DISPLAY_VERTICAL_LINE_SPACE)
      current_line = current_line + 1

      dpg.draw_text(
        parent = self._terminal_layer_id,
        pos   = (TERM_DISPLAY_LEFT_OFFSET, vertical_offset),
        text  = buffer_line.format(), 
        color = (204, 204, 204),
        size  = DEFAULT_FONT_SIZE
      )

    # Draw the Command Prompt.
    vertical_offset = TERM_DISPLAY_INITIAL_TOP_OFFSET + \
        (current_line * TERM_DISPLAY_LINE_HEIGHT) + \
        (current_line * TERM_DISPLAY_VERTICAL_LINE_SPACE)
    
    # 1. Draw the green '>'. 
    dpg.draw_text(
      parent = self._terminal_layer_id,
      pos   = (TERM_DISPLAY_LEFT_OFFSET, vertical_offset),
      text  = TERM_ACTIVE_PROMPT_INDICATOR, 
      color = Colors.green.value,
      size  = DEFAULT_FONT_SIZE
    )

    # 2. Draw the active prompt text.
    dpg.draw_text(
      parent = self._terminal_layer_id,
      pos   = (TERM_DISPLAY_LEFT_OFFSET + DEFAULT_FONT_SIZE, vertical_offset),
      text  = screen_buffer.active_prompt, 
      color = (204, 204, 204),
      size  = DEFAULT_FONT_SIZE
    )
    
    # 3. Draw the block prompt.
    dpg.draw_text(
      parent = self._terminal_layer_id,
      pos   = (TERM_DISPLAY_LEFT_OFFSET + DEFAULT_FONT_SIZE + screen_buffer.cursor_location * TERM_FONT_ADVANCE, vertical_offset),
      text  = TERM_PROMPT_CHAR, 
      color = (204, 204, 204),
      size  = DEFAULT_FONT_SIZE
    )

    # 4. If the prompt is over a character, draw the character on top of the block.
    if screen_buffer.cursor_location < len(screen_buffer.active_prompt):
      highlighted_char = screen_buffer.active_prompt[screen_buffer.cursor_location]
      dpg.draw_text(
        parent = self._terminal_layer_id,
        pos   = (TERM_DISPLAY_LEFT_OFFSET + DEFAULT_FONT_SIZE + screen_buffer.cursor_location * TERM_FONT_ADVANCE, vertical_offset),
        text  = highlighted_char, 
        color = Colors.black.value,
        size  = DEFAULT_FONT_SIZE
      )
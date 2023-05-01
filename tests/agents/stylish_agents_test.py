
from agents_playground.agents.default.default_agent_style import DefaultAgentStyle
from agents_playground.renderers.color import BasicColors

class TestStylishAgents:
  def test_agents_have_style(self) -> None:
    agent_style = DefaultAgentStyle()
    assert agent_style.stroke_thickness      == 1.0
    assert agent_style.stroke_color          == BasicColors.black.value
    assert agent_style.fill_color            == BasicColors.blue.value
    assert agent_style.aabb_stroke_color     == BasicColors.red.value
    assert agent_style.aabb_stroke_thickness == 1.0
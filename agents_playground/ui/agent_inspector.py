import dearpygui.dearpygui as dpg
from agents_playground.agents.spec.agent_spec import AgentLike

from agents_playground.ui.utilities import add_tree_table


class AgentInspectorWindow:
    def __init__(self) -> None:
        pass

    def launch(self, agent: AgentLike, height: int) -> None:
        with dpg.window(label="Agent Inspector", width=660, height=height):
            add_tree_table(label="Identity", data=agent.identity)
            add_tree_table(label="State", data=agent.agent_state)
            add_tree_table(label="Systems", data=agent.internal_systems)
            add_tree_table(label="Memory", data=agent.memory)
            add_tree_table(label="Style", data=agent.style)
            add_tree_table(label="Physicality", data=agent.physicality)
            add_tree_table(label="Position", data=agent.position)
            add_tree_table(label="Movement", data=agent.movement)

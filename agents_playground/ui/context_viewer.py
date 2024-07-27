from types import SimpleNamespace
from typing import Callable, List
import dearpygui.dearpygui as dpg
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.renderers.color import BasicColors

from agents_playground.simulation.context import SimulationContext
from agents_playground.ui.utilities import add_table_of_namespaces, add_tree_table


class ContextViewerWindow:
    def launch(
        self, context: SimulationContext, height: int, inspect_agent_callback: Callable
    ) -> None:
        with dpg.window(label="Context Viewer", width=660, height=height):
            add_tree_table(
                label="General",
                data={
                    "Parent Window Size": context.parent_window,
                    "Canvas Size": context.canvas,
                },
            )
            add_tree_table(label="Details", data=context.details)

            with dpg.tree_node(label="Scene"):
                add_tree_table(
                    label="General",
                    data={
                        "Cell Size": context.scene.cell_size,
                        "Cell Center X Offset": context.scene.cell_center_x_offset,
                        "Cell Center Y Offset": context.scene.cell_center_y_offset,
                    },
                )

                with dpg.tree_node(label="Agents"):
                    with dpg.table(
                        header_row=True,
                        policy=dpg.mvTable_SizingFixedFit,
                        row_background=True,
                        borders_innerH=True,
                        borders_outerH=True,
                        borders_innerV=True,
                        borders_outerV=True,
                    ):
                        dpg.add_table_column(label="Actions", width_fixed=True)
                        dpg.add_table_column(label="Id", width_fixed=True)
                        dpg.add_table_column(label="Render ID", width_fixed=True)
                        dpg.add_table_column(label="TOML ID", width_fixed=True)
                        dpg.add_table_column(label="AABB ID", width_fixed=True)
                        dpg.add_table_column(label="Selected", width_fixed=True)
                        dpg.add_table_column(label="Visible", width_fixed=True)
                        dpg.add_table_column(
                            label="Current Action State", width_fixed=True
                        )
                        dpg.add_table_column(label="Location", width_fixed=True)
                        agent: AgentLike
                        for agent in context.scene.agents.values():
                            selected_color = (
                                BasicColors.green.value
                                if agent.agent_state.selected
                                else BasicColors.red.value
                            )
                            visible_color = (
                                BasicColors.green.value
                                if agent.agent_state.visible
                                else BasicColors.red.value
                            )
                            with dpg.table_row():
                                dpg.add_button(
                                    label="inspect",
                                    callback=inspect_agent_callback,
                                    user_data=agent.identity.id,
                                )
                                dpg.add_text(str(agent.identity.id))
                                dpg.add_text(str(agent.identity.render_id))
                                dpg.add_text(str(agent.identity.community_id))
                                dpg.add_text(str(agent.identity.aabb_id))
                                dpg.add_text(
                                    str(agent.agent_state.selected),
                                    color=selected_color,
                                )
                                dpg.add_text(
                                    str(agent.agent_state.visible), color=visible_color
                                )
                                dpg.add_text(
                                    agent.agent_state.current_action_state.__repr__()
                                )
                                dpg.add_text(agent.position.location.__repr__())

                with dpg.tree_node(label="Entities"):
                    for group_name, entity_grouping in context.scene.entities.items():
                        rows: List[SimpleNamespace] = list(entity_grouping.values())
                        add_table_of_namespaces(
                            label=group_name,
                            columns=list(rows[0].__dict__.keys()),
                            rows=rows,
                        )

                if len(context.scene.nav_mesh._junctions) > 0:
                    with dpg.tree_node(label="Navigation Mesh"):
                        junction_rows: List[SimpleNamespace] = list(
                            context.scene.nav_mesh.junctions()
                        )
                        add_table_of_namespaces(
                            label="Junctions",
                            columns=list(junction_rows[0].__dict__.keys()),
                            rows=junction_rows,
                        )

                add_tree_table(label="Paths", data=context.scene.paths)
                add_tree_table(label="Layers", data=context.scene.layers)

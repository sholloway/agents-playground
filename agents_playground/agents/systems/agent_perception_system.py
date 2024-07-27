from typing import Dict
from agents_playground.agents.byproducts.definitions import Stimuli
from agents_playground.agents.byproducts.sensation import Sensation
from agents_playground.agents.default.default_agent_system import SystemWithByproducts
from agents_playground.agents.memory.memory import Memory
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.agents.spec.agent_system import SystemMemoryError
from agents_playground.fp.containers import FPList
from agents_playground.simulation.tag import Tag


class AgentPerceptionSystem(SystemWithByproducts):
    """
    Processes stimuli. What the agent is aware of.
    The organization, identification, and interpretation of sensory information in
    order to represent and understand the presented information or environment.
    """

    def __init__(self, output_memory_container: str = "sensory_memory") -> None:
        super().__init__(
            name="agent_perception", byproduct_defs=[], internal_byproduct_defs=[]
        )
        self._output_memory_container = output_memory_container

    def _before_subsystems_processed_pre_state_change(
        self,
        characteristics: AgentCharacteristics,
        parent_byproducts: dict[str, list],
        other_agents: Dict[Tag, AgentLike],
    ) -> None:
        """
        Collect all sensory information that the agent is experiencing.
        """
        try:
            if Stimuli.name in parent_byproducts:
                memory_store: FPList[Memory] = characteristics.memory[
                    self._output_memory_container
                ].unwrap()
                sensation: Sensation
                for sensation in parent_byproducts[Stimuli.name]:
                    memory_store.append(Memory(sensation))
        except KeyError:
            error_msg = f"AgentPerceptionSystem requires the agent has a MemoryContainer named {self._output_memory_container}."
            raise SystemMemoryError(error_msg)

from operator import contains
from typing import Tuple
import pytest
from pytest_mock import MockerFixture
from agents_playground.agents.byproducts.sensation import Sensation, SensationType

from agents_playground.agents.default.default_agent import DefaultAgent
from agents_playground.agents.default.default_agent_state import DefaultAgentState
from agents_playground.agents.default.default_agent_system import DefaultAgentSystem
from agents_playground.agents.default.named_agent_state import NamedAgentActionState
from agents_playground.agents.memory.agent_memory_model import AgentMemoryModel
from agents_playground.agents.memory.memory import Memory
from agents_playground.agents.memory.memory_container import MemoryContainer
from agents_playground.agents.no_agent import NoAgent
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.agents.systems.agent_nervous_system import AgentNervousSystem
from agents_playground.agents.systems.agent_perception_system import (
    AgentPerceptionSystem,
)
from agents_playground.agents.systems.agent_visual_system import VisualSensation
from agents_playground.containers.ttl_store import TTLStore
from agents_playground.fp.containers import FPList
from agents_playground.simulation.tag import Tag

"""
Test an agent's ability to have cognition (i.e. mental capacity).
"""


@pytest.fixture
def nervous_agent(mocker: MockerFixture) -> AgentLike:
    """
    Create an agent that has a nervous system wired up.
    """
    root_system = DefaultAgentSystem(name="root-system")
    root_system.register_system(AgentNervousSystem())
    return DefaultAgent(
        initial_state=mocker.Mock(),
        style=mocker.Mock(),
        identity=mocker.Mock(),
        physicality=mocker.Mock(),
        position=mocker.Mock(),
        movement=mocker.Mock(),
        agent_memory=AgentMemoryModel(
            sensory_memory=MemoryContainer(FPList[Memory]()),
            working_memory=MemoryContainer(TTLStore[Memory]()),
            long_term_memory=MemoryContainer(FPList[Memory]()),
        ),
        internal_systems=root_system,
    )


@pytest.fixture
def perceptive_agent(nervous_agent: AgentLike) -> AgentLike:
    nervous_agent.internal_systems.register_system(AgentPerceptionSystem())
    return nervous_agent


class TestAgentPerception:
    def test_agent_sees_something(self, perceptive_agent: AgentLike) -> None:
        # Confirm that the visual system is in place.
        assert (
            perceptive_agent.internal_systems.subsystems.agent_nervous_system.subsystems.visual_system
            is not None
        )

        no_agent = NoAgent()

        # Process the agent's systems.
        perceptive_agent.transition_state(other_agents={0: no_agent})

        # Confirm the agent saw something.
        # Need to confirm the sensory memory contains a visual sensation.
        assert (
            VisualSensation(seen=tuple([no_agent.identity.id]))
            in perceptive_agent.memory["sensory_memory"]
        )
        assert len(perceptive_agent.memory["sensory_memory"]) > 0

    @pytest.mark.skip(reason="Hearing system is not implemented yet.")
    def test_agent_hears_something(
        self, mocker: MockerFixture, perceptive_agent: AgentLike
    ) -> None:
        # Confirm that the visual system is in place.
        assert (
            perceptive_agent.internal_systems.subsystems.agent_nervous_system.subsystems.auditory_system
            is not None
        )

        # TODO: Setup something for the agent to hear.

        # Process the agent's systems.
        perceptive_agent.transition_state({})

        # Confirm the agent saw something.
        # Need to confirm the sensory memory contains a visual sensation.
        # assert Sensation(SensationType.Audible) in perceptive_agent.memory.sensory_memory.memory_store

    @pytest.mark.skip(reason="Somatosensory system is not implemented yet.")
    def test_agent_touches_something(
        self, mocker: MockerFixture, perceptive_agent: AgentLike
    ) -> None:
        # Confirm that the visual system is in place.
        assert (
            perceptive_agent.internal_systems.subsystems.agent_nervous_system.subsystems.somatosensory_system
            is not None
        )

        # TODO: Setup something for the agent to touch.

        # Process the agent's systems.
        perceptive_agent.transition_state({})

        # Confirm the agent saw something.
        # Need to confirm the sensory memory contains a visual sensation.
        # assert Sensation(SensationType.Tactile) in perceptive_agent.memory.sensory_memory.memory_store

    @pytest.mark.skip(reason="Auditory system is not implemented yet.")
    def test_agent_smells_something(
        self, mocker: MockerFixture, perceptive_agent: AgentLike
    ) -> None:
        # Confirm that the visual system is in place.
        assert (
            perceptive_agent.internal_systems.subsystems.agent_nervous_system.subsystems.olfactory_system
            is not None
        )

        # TODO: Setup something for the agent to smell.

        # Process the agent's systems.
        perceptive_agent.transition_state({})

        # Confirm the agent saw something.
        # Need to confirm the sensory memory contains a visual sensation.
        # assert Sensation(SensationType.Smell) in perceptive_agent.memory.sensory_memory.memory_store

    @pytest.mark.skip(reason="Gustatory system is not implemented yet.")
    def test_agent_tastes_something(
        self, mocker: MockerFixture, perceptive_agent: AgentLike
    ) -> None:
        # Confirm that the visual system is in place.
        assert (
            perceptive_agent.internal_systems.subsystems.agent_nervous_system.subsystems.gustatory_system
            is not None
        )

        # TODO: Setup something for the agent to taste.

        # Process the agent's systems.
        perceptive_agent.transition_state({})

        # Confirm the agent saw something.
        # Need to confirm the sensory memory contains a visual sensation.
        # assert Sensation(SensationType.Taste) in perceptive_agent.memory.sensory_memory.memory_store

    @pytest.mark.skip(reason="Vestibular system is not implemented yet.")
    def test_agent_vestibular(
        self, mocker: MockerFixture, perceptive_agent: AgentLike
    ) -> None:
        # Confirm that the visual system is in place.
        assert (
            perceptive_agent.internal_systems.subsystems.agent_nervous_system.subsystems.vestibular_system
            is not None
        )

        # TODO: Setup something for the agent to experience.

        # Process the agent's systems.
        perceptive_agent.transition_state({})

        # Confirm the agent saw something.
        # Need to confirm the sensory memory contains a visual sensation.
        # assert Sensation(SensationType.Vestibular) in perceptive_agent.memory.sensory_memory.memory_store

from typing import List
from agents_playground.actions.agent_action import AgentAction
from agents_playground.simulation.tag import Tag


class AgentPath:
    def __init__(self, id: Tag, steps: List[AgentAction] = []) -> None:
        self._steps: List[AgentAction] = steps
        self._id: Tag = id

    @property
    def id(self) -> Tag:
        return self._id

    def step(self, step_index: int) -> AgentAction:
        return self._steps[step_index]

    def __iter__(self):
        return self._steps.__iter__()

    # def __next__(self):
    #   return self._steps.__next__()

    def __len__(self) -> int:
        return len(self._steps)

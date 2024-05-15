from abc import abstractmethod
from typing import Protocol

"""
Placeholders for cognitive processing.
"""


class AgentCognitiveProcess(Protocol):
    @abstractmethod
    def think(self) -> None: ...


class Thought(AgentCognitiveProcess):
    def think(self) -> None:
        return


class Imagination(AgentCognitiveProcess):
    def think(self) -> None:
        return


class Judgement(AgentCognitiveProcess):
    def think(self) -> None:
        return


class Evaluation(AgentCognitiveProcess):
    def think(self) -> None:
        return


class Reasoning(AgentCognitiveProcess):
    def think(self) -> None:
        return


class Computation(AgentCognitiveProcess):
    def think(self) -> None:
        return


class ProblemSolving(AgentCognitiveProcess):
    def think(self) -> None:
        return


class DecisionMaking(AgentCognitiveProcess):
    def think(self) -> None:
        return


class Comprehension(AgentCognitiveProcess):
    def think(self) -> None:
        return


class Speaking(AgentCognitiveProcess):
    def think(self) -> None:
        return


class Writing(AgentCognitiveProcess):
    def think(self) -> None:
        return


class FormationOfKnowledge(AgentCognitiveProcess):
    def think(self) -> None:
        return

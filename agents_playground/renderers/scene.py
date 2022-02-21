from dataclasses import dataclass
from typing import Dict

from agents_playground.simulation.tag import Tag
from agents_playground.agents.agent import Agent
from agents_playground.agents.path import Path
@dataclass
class Scene:
  agents: Dict[Tag, Agent]
  paths: Dict[Tag, Path]

  def __init__(self) -> None:
    self.agents = dict()
    self.paths = dict()

  def add_agent(self, agent: Agent) -> None:
    self.agents[agent.id] = agent

  def add_path(self, path: Path) -> None:
    self.paths[path.id] = path
    
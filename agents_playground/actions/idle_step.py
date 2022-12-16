"""
What is Idle?
It is a path instruction that indicates the agent should 
not move for a certain number of frames.

How does this work if logic to do something is encapsulated in an Action?
"""
from agents_playground.actions.agent_action import AgentAction
from agents_playground.agents.agent import Agent


class IdleStep(AgentAction):
  frames: int
  
  def _perform(self, agent: Agent, **data):
    pass
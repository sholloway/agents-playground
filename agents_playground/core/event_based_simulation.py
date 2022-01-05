from time import sleep

from agents_playground.core.simulation import Simulation, SimulationState
from agents_playground.core.scheduler import JobScheduler
from agents_playground.core.time_utilities import TIME_PER_UPDATE, TimeInMS, TimeUtilities

class EventBasedSimulation(Simulation):
  def __init__(self) -> None:
      super().__init__()
      self._scheduler: JobScheduler = JobScheduler()

  # Override the sim_loop to be event based.
  def _sim_loop(self, **data):
    """The thread callback that processes a simulation tick.
    
    Using the definitions in agents_playground.core.time_utilities, this ensures
    a fixed time for scheduled events to be ran. Rendering is handled automatically
    via DataPyUI (note: VSync is turned on when the Viewport is created.)

    For 60 FPS, TIME_PER_UPDATE is 5.556 ms.
    """

    previous_time: TimeInMS = TimeUtilities.now()
    lag: TimeInMS = 0
    while self.simulation_state is not SimulationState.ENDED:
      if self.simulation_state is SimulationState.RUNNING:
        current_time: TimeInMS = TimeUtilities.now()
        elapsed_time: TimeInMS = current_time - previous_time
        previous_time = current_time
        lag += elapsed_time
        # process_input()
        while lag >= TIME_PER_UPDATE:
          self._scheduler.run(TIME_PER_UPDATE)
          lag -= TIME_PER_UPDATE
        self._sim_loop_tick(**data) #render()
      else:
        # The sim isn't running so don't keep checking it.
        sleep(self._sim_stopped_check_time) 

from enum import Enum


class SimulationState(Enum):
    INITIAL = "simulation:state:initial"
    RUNNING = "simulation:state:running"
    STOPPED = "simulation:state:stopped"
    ENDED = "simulation:state:ended"


SimulationStateTable = {
    SimulationState.INITIAL: SimulationState.RUNNING,
    SimulationState.RUNNING: SimulationState.STOPPED,
    SimulationState.STOPPED: SimulationState.RUNNING,
}

RUN_SIM_TOGGLE_BTN_START_LABEL = "Start"
RUN_SIM_TOGGLE_BTN_STOP_LABEL = "Stop"

SimulationStateToLabelMap = {
    SimulationState.INITIAL: RUN_SIM_TOGGLE_BTN_START_LABEL,
    SimulationState.RUNNING: RUN_SIM_TOGGLE_BTN_STOP_LABEL,
    SimulationState.STOPPED: RUN_SIM_TOGGLE_BTN_START_LABEL,
}

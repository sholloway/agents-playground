from dataclasses import dataclass, field

from agents_playground.core.samples import Samples

@dataclass
class SimulationStatistics:
    per_frame_samples: dict[str, Samples] = field(init=False)

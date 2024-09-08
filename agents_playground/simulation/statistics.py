from dataclasses import dataclass, field

from agents_playground.core.samples import SamplesDistribution

@dataclass
class SimulationStatistics:
    per_frame_samples: dict[str, SamplesDistribution] = field(init=False)

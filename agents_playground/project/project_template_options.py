from dataclasses import dataclass, field

@dataclass
class ProjectTemplateOptions:
  project_name: str = field(init=False, default='')
  simulation_title: str = field(init=False, default='')
  simulation_description: str = field(init=False, default='')
  project_parent_directory: str = field(init=False, default='')
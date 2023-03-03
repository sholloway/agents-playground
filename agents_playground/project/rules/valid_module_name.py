
from agents_playground.project.project_loader_error import ProjectLoaderError
from agents_playground.project.rules.project_validator import ProjectValidator

class ValidModuleName(ProjectValidator):
  """
  Per Pep-8: https://peps.python.org/pep-0008/#package-and-module-names
  Modules should have short, all-lowercase names. 
  Underscores can be used in the module name if it improves readability.
  """
  def validate(self, module_name: str, module_path: str) -> bool:
    if not module_name.islower() or not module_name.isidentifier():
      raise ProjectLoaderError(f'The module name {module_name} is not formatted correctly. Modules must be all lowercase. Underscores are allowed.')
    return True
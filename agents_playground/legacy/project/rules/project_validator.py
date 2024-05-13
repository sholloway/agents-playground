from abc import ABC, abstractmethod

class ProjectValidator(ABC):
    @abstractmethod
    def validate(self, module_name: str, module_path: str) -> bool:
      """
      Validates a project for a specific rule.
      """    
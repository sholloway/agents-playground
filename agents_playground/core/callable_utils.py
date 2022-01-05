from types import FunctionType
from typing import Callable, Optional

class CallableUtility:
  @staticmethod
  def invoke(job: Optional[Callable], data: Optional[dict] = None) -> None:
    if callable(job) or isinstance(job, FunctionType):
      if data:
        job(**data)
      else:
        job()
from types import FunctionType
from typing import Any, Callable, Optional


class CallableUtility:
    @staticmethod
    def invoke(job: Any, data: Optional[dict] = None) -> None:
        if callable(job) or isinstance(job, FunctionType):
            if data:
                job(**data)
            else:
                job()

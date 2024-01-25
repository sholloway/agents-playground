
from types import SimpleNamespace

from agents_playground.legacy.scene.parsers.scene_parser_exception import SceneParserException

def require_attr(scene_data: SimpleNamespace, attribute: str, err_msg: str) -> None:
  """Raises an exception is an attribute is not present."""
  if not hasattr(scene_data, attribute):
    raise SceneParserException(err_msg)
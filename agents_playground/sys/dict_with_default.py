from typing import MutableMapping, TypeVar

DictKey = TypeVar('DictKey')
DictValue = TypeVar('DictValue')

class DictWithDefault(dict, MutableMapping[DictKey, DictValue]):
  default_value: DictValue
  
  def __init__(self, **kwargs) -> None:
    super(DictWithDefault, self).__init__(**kwargs)

  def __getitem__(self, key: DictKey):
    if key in self:
      return super(DictWithDefault, self).__getitem__(key)
    elif self.default_value:
      return self.default_value
    else:
      raise KeyError(f'The key {key} was not found and the default value was not')
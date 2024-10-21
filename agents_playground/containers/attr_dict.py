from collections import UserDict
from typing import Any


class AttrDict(UserDict):
    """
    Behaves like a Python dict but enables setting attributes
    using dot notation.

    Note that the UserDict stores values in the data attribute
    with is an actual dict instance.
    """

    def __getitem__(self, key: str) -> Any:
        """
        Enables fetching attributes dictionary style.
        """
        return self.data[key]

    def __getattr__(self, key: str) -> Any:
        """
        Enables fetching attributes via dot notation.
        """
        return self.__getitem__(key)

    def __setattr__(self, key: str, value: Any):
        """
        Enables setting attributes via dot notation.
        """
        if key == "data":
            # Prevent overwriting the data attribute that stores
            # the class attributes.
            return super().__setattr__(key, value)
        return self.__setitem__(key, value)
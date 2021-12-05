from abc import ABC, abstractmethod
from typing import List

class Observer(ABC):
  @abstractmethod
  def update(self, msg:str) -> None:
    """Receives a notification message from an observable object."""    

    
class Observable:
  """
  A class that notifies subscribers of events.
  """
  def __init__(self) -> None:
    self._observers: List[Observer] = []

  def attach(self, observer: Observer) -> None:
    """
    Attach an observer to the subject.
    """
    self._observers.append(observer)

    
  def detach(self, observer: Observer) -> None:
    """
    Detach an observer from the subject.
    """
    if observer in self._observers:
      self._observers.remove(observer)

  
  def notify(self, msg: str) -> None:
    """
    Notify all observers about an event.
    """
    for observer in self._observers:
      observer.update(msg)
from agents_playground.core.observe import Observer, Observable

class FakeObserver(Observer):
  def __init__(self) -> None:
    super().__init__()
    self.update_called_count = 0

  def update(self, msg:str) -> None:
    self.update_called_count += 1
  

class TestObserverPattern:
  def test_attaching_registers_observers(self):
    observer_a = FakeObserver()
    observer_b = FakeObserver()
    observer_c = FakeObserver()

    observable = Observable()
    assert len(observable._observers) == 0

    observable.attach(observer_a)
    assert len(observable._observers) == 1
    
    observable.attach(observer_b)
    assert len(observable._observers) == 2

    observable.attach(observer_c)
    assert len(observable._observers) == 3

    assert observer_a in observable._observers
    assert observer_b in observable._observers
    assert observer_c in observable._observers

  def test_prevent_duplicate_registration(self):
    observer_a = FakeObserver()
    observable = Observable()
    observable.attach(observer_a)
    observable.attach(observer_a)
    observable.attach(observer_a)
    observable.attach(observer_a)
    observable.attach(observer_a)
    assert len(observable._observers) == 1
    assert observer_a in observable._observers

  def test_stuff(self):
    observer_a = FakeObserver()
    observer_b = FakeObserver()
    observer_c = FakeObserver()
    observable = Observable()

    observable.attach(observer_a)
    observable.attach(observer_b)
    observable.attach(observer_c)

    assert observer_a.update_called_count == 0
    assert observer_b.update_called_count == 0
    assert observer_c.update_called_count == 0

    observable.notify('important msg')
    
    assert observer_a.update_called_count == 1
    assert observer_b.update_called_count == 1
    assert observer_c.update_called_count == 1

    observable.notify('important msg')
    observable.notify('important msg')
    observable.notify('important msg')

    assert observer_a.update_called_count == 4
    assert observer_b.update_called_count == 4
    assert observer_c.update_called_count == 4

  def test_detach(self):
    observer_a = FakeObserver()
    observable = Observable()
    observable.attach(observer_a)

    assert len(observable._observers) == 1
    assert observer_a in observable._observers

    observable.detach(observer_a)
    assert len(observable._observers) == 0
    assert observer_a not in observable._observers
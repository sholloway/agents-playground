Profiling

---

## FAQ

### How can I measure the size of an object?

The sys.getsizeof(...) function returns the size in bytes of a given object.

```python
import sys

x = {'a': 123, 'b': 'hello world'}
sys.getsizeof(x)
```

There is a convenience function in profile_tools.py that will log the size
at the DEBUG level.

```python
from profile_tools import size

x = {'a': 123, 'b': 'hello world'}
size('x', x)
# This will log something like:
# 2021-11-28 10:47:58,227 agent_playground.main DEBUG x's size: 104 bytes
```

### How can I measure simple runtime of a piece of code?

Use time.perf_counter_ns() to measure how long something took.

```python
import time

start = time.perf_counter_ns()
do_a_bunch_of_stuff()
end  = time.perf_counter_ns()
duration = end - start
```

There is a convenience decorator in profile_tools.py.

```python
from profile_tools import timer

@timer
do_a_bunch_of_stuff()

# This will log at the DEBUG level something like:
# 021-11-28 10:02:22,610 agent_playground.main DEBUG do_a_bunch_of_stuff runtime 3.485257938 seconds | 3485.257938 ms
```

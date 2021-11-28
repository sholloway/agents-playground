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

### How can I measure simple runtime of a piece of code?

Use time.perf_counter_ns() to measure how long something took.

```python
import time

start = time.perf_counter_ns()
do_a_bunch_of_stuff()
end  = time.perf_counter_ns()
duration = end - start
```

### Is there a decorator available to simplify that?

You better believe it. ;)

```python
from profile_tools import timer

@timer
do_a_bunch_of_stuff()

# This will log at the DEBUG level something like:
# 021-11-28 10:02:22,610 agent_playground.main DEBUG do_a_bunch_of_stuff runtime 3.485257938 seconds | 3485.257938 ms

```

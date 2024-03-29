# Dependencies

---

## Runtime Dependencies

- Python 3.11: The runtime language.
- [DearPyGui](https://dearpygui.readthedocs.io/en/latest/index.html): A GUI framework.
- [psutil](): A hardware monitoring module.
- [more-itertools]()

## Development Dependencies

- [MyPy](https://mypy.readthedocs.io/en/stable/index.html): Static type checker.
- [pudb](https://github.com/inducer/pudb): An interactive terminal debugger.
- [py-spy](https://github.com/benfred/py-spy): A sampling profiler.
- [pytest](https://docs.pytest.org/en/6.2.x/contents.html): Unit testing
- [pytest-mock](https://github.com/pytest-dev/pytest-mock): Mocking and Stubs
- [bpython](https://www.bpython-interpreter.org/): A fancy interactive Python shell.
- [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/): Calculates test coverage.
- [pdoc](https://pdoc.dev/): Generates code documentation.
- [matplotlib](https://matplotlib.org/): A Python visualization library. I only use this when benchmarking.
- [line-profiler](https://github.com/pyutils/line_profiler): A Python profiler.

## Update Dependencies.
We can see the outdated dependencies by running the below command.
```shell
poetry show -l
```

Use the poetry __add__ command to update the version of a dependencies.
```shell
poetry add "mypy==1.5.1"
```

Then run the poetry __update__ command to install the updated version.
```shell
poetry update
```

Then verify the project is ok.
```shell
make check test run
```

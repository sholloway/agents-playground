Testing

---

The project uses [pytest](https://docs.pytest.org/en/6.2.x/contents.html) for unit tests.

- [FAQ](#faq)
  - [How to handle mocks?](#how-to-handle-mocks)
  - [How are tests identified?](#how-are-tests-identified)
  - [What are all of the command line options for pytest?](#what-are-all-of-the-command-line-options-for-pytest)
  - [What are the test configuration options for the pyproject.toml file?](#what-are-the-test-configuration-options-for-the-pyprojecttoml-file)

## FAQ

### How to handle mocks?

Mocks are provided using the [pytest-mock](https://github.com/pytest-dev/pytest-mock)
wrapper around the [unittest.mock](https://docs.python.org/3.9/library/unittest.mock.html) module.

### How are tests identified?

See the pytest [test discovery](https://docs.pytest.org/en/6.2.x/goodpractices.html#test-discovery) rules.

### What are all of the command line options for pytest?

See the [docs](https://docs.pytest.org/en/6.2.x/reference.html#command-line-flags).

### What are the test configuration options for the pyproject.toml file?
See the [docs](https://docs.pytest.org/en/6.2.x/reference.html#configuration-options).

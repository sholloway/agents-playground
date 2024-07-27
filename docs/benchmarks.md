# Benchmarks

---

## Tooling
The package [pytest-benchmark](https://pypi.org/project/pytest-benchmark/) is used for performance benchmarking.

## Writing Benchmark Tests
Tests are organized in the ./benchmarks folder of the project.
They follow the pytest conventions.

## Running Tests
All benchmarks can be run on the console with `make benchmark`.

Specific test suites can be run by specifying the path to the test file.
```bash
poetry run pytest ./benchmarks/spatial/numerical_test.py --benchmark-columns="min, mean, max, median, stddev, iqr, outliers, ops, rounds, iterations";
```

## Calculating Percentiles 
The table output of pytest-benchmark does not include percentiles. 
However, you can get the performance distribution of minimum, P25, P50, P75, and Maximum
by generating boxplots.

To generate all of the performance boxplots run `make viz_benchmark`.
An SVG file will be created in folder ./benchmark_histograms. The file will be named 
with the timestamp of when it was run.

Boxplots can be created for a specific test suite by providing the path to the test.

```shell
poetry run pytest ./benchmarks/spatial/numerical_test.py --benchmark-histogram=./benchmark_histograms/$(date +%m_%d_%y@%H_%M)/
```

## How to Interpret Results
Running `make benchmark` outputs a table with the several columns. Here are the definitions
for each column.

| Column     | Definition |
|------------|------------|
| min        | The fastest measured speed for the operation under test. |
| mean       | The average measured speed for the operation under test. |
| max        | The slowest measured speed for the operation under test. |
| median     | The 50th percentile.                                     |
| stddev     | The standard deviation. This describes how the samples are clustered around the mean. A low number implies performance consistency. |
| iqr        | The interquartile. This is the difference between the 75th-percentile and the 25th-percentile.|
| outliers   | The number of outliers. See the section below on outliers for more details. |
| ops        | Operations per second. The number of times the function under test was invoked in a second. |
| rounds     | A round is a set of iterations. This is the number of sets of iterations that were run. |
| iterations | The total number of times an individual benchmark function was run. |

The columns min, mean, max, median, stddev, iqr, and ops all contain a number followed 
by an enclosed number (X). The enclosed number is the ratio for for that value compares
to the other rows. Look at the Min column in the below table for example.

| Name (time in ns) | Min              |            
|-------------------|------------------|
| test_ints         | 32.1371 (1.0)    |
| test_floats       | 33.7971 (1.05)   |
| test_decimals     | 53.9600 (1.68)   |
| test_fractions    | 624.9757 (19.45) |

The first row has the (1) value. That indicates that is the fastest value and is used 
as the baseline to compare the others. The last row has the value (19.45). That indicates
the ratio of it's measurement to the first row. It's saying that the last row is 19.45x
more than the first row.

## Rounds and Iterations
The pytest-benchmark modules runs the function under test many many times. Each time 
it is run that is called an _iteration_. A set of iterations is called a _round_.

So a given function will run `rounds * iterations` times. 

The below snippet shows the gist of how the package runs tests ([original source](https://github.com/ionelmc/pytest-benchmark/issues/186)). 
```python
# First warm up.
for _ in range(warmup_rounds):
    for _ in range(iterations):
        function_to_benchmark(*args, **kwargs)

# Run the benchmark
for _ in range(rounds):
    start = timer()
    for _ in range(iterations):
        function_to_benchmark(*args, **kwargs)
    end = timer()
    duration = end - start
```

The performance metrics of a round are averaged together to compute the results tables. 

## Operations per Second
The 'ops' column in the benchmark results stands for Operations per Second. 
The output is formatted using the below code ([source](https://github.com/ionelmc/pytest-benchmark/blob/master/src/pytest_benchmark/utils.py#L457)).

```python
def operations_unit(value):
    if value > 1e6:
        return 'M', 1e-6
    if value > 1e3:
        return 'K', 1e-3
    return '', 1.0
```

That means, if the Ops column reads "OPS (Mops/s)" then the values are million operations 
per second. So the value 31.3192 Mops/s conveys that the operation under test was 
invoked 31.3192 million times per second on average.

## Outliers
The outliers column is used to communicate two different metrics separated by a ";".
- The count of standard deviation outliers. 
- The count of tukey outliers.

A standard deviation outlier is defined as a timing value outside the range `(Mean - StdDev, Mean + StdDev)`.
A [tukey outlier](https://en.wikipedia.org/wiki/Outlier#Tukey's_fences) is a timing value that falls outside of the range of `(P25 - 1.5 * IQR, P75 + 1.5 * IQR)`.

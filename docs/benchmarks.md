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
poetry run pytest ./benchmarks/spatial/numerical_test.py \
    --benchmark-columns="min, mean, max, median, stddev, iqr, outliers, ops, rounds iterations";
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
Running `make benchmark` outputs a table with the several columns. Here is the definition
for each column.

| Column     | Definition |
|------------|------------|
| min        | The fastest measured speed for the operation under test. |
| mean       | The average measured speed for the operation under test. |
| max        | The slowest measured speed for the operation under test. |
| median     | The 50th percentile.                                     |
| stddev     | The standard deviation. This describes how the samples are clustered around the mean. A low number implies performance consistency. |
| iqr        | The interquartile. This is the difference between the 75th-percentile and the 25th-percentile.|
| outliers   | Two values separated by a ';'. They are 1 Standard Deviation from Mean, The difference between 1st Quartile and 3rd Quartile. |
| ops        | |
| rounds     | |
| iterations | |

The columns min, mean, max, median, stddev, IQR, and Ops all contain a number followed 
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


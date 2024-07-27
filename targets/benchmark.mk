DEFAULT_BENCHMARK_COLS="min, mean, max, median, stddev, iqr, outliers, ops, rounds, iterations"

# Run all of the benchmark tests.
# 
# Outputs a table with the following columns:
# 	min: The fastest round.
# 	mean: The average round
# 	max: The slowest round
#		median: The 50th-percentile.
#		stddev: The standard deviation. Lower values suggest more consistent performance.
#		iqr: (Interquartile Range): A statistical measure that represents the range 
#         between the first quartile (25th percentile) and the third quartile 
#         (75th percentile) of a dataset. A larger IQR could indicate more 
#					variability in performance, while a smaller IQR suggests more consistent performance.
#		outliers: Data points that significantly deviate from the rest of the data in a dataset.
#		ops: 1000 operations per second. Higher the better.
#		rounds: The number of times a benchmark round was ran.
#		iterations: The number of iterations per round.
run-benchmarks:
	@( \
	source .venv/bin/activate; \
	poetry run pytest ./benchmarks --benchmark-columns=$(DEFAULT_BENCHMARK_COLS); \
	)

# Run the benchmarks identified with the BENCHMARK_THIS
# Example:
# BENCHMARK_THIS=./benchmarks/spatial/numerical_test.py make benchmark_this
run-benchmark-this:
	@( \
	source .venv/bin/activate; \
	poetry run pytest $(BENCHMARK_THIS) --benchmark-columns=$(DEFAULT_BENCHMARK_COLS); \
	)

# Run the benchmarks and generate histograms for each test group.
# Use the -m option to only generate an image for a specific group name.
run-benchmark-boxplots:
	poetry run pytest ./benchmarks --benchmark-histogram=./benchmark_histograms/$(shell date +%m_%d_%y@%H_%M)/
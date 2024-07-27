include targets/*.mk

# Phony targets are targets that are always out-of-date (i.e. they'll always run). 
.PHONY: env setup-pip setup-project 
.PHONY: run run_sim run_old run_dev 
.PHONY: test test_debug cov 
.PHONY: check format format_tests 
.PHONY: stats_size stats_scan 
.PHONY: doc debug build 
.PHONY: profile_flame_graph profile_top profile_function profile_test 
.PHONY: benchmark benchmark_boxplots

# Don't show the change directory messages.
MAKEFLAGS += --no-print-directory

# By default, if we just run "make" then launch the application. 
.DEFAULT_GOAL=help 

# Help (help.mk)
help: run-help

# Project Bootstrapping (env.mk)
env: env-shell 
setup-pip: env-setup
setup-project: env-install-dependencies

# Run the Application (run.mk)
run: run-default
run_sim: run-sim
run_old: run-classic
run_dev: run-dev
shell: run-shell # (shell.mk)

# Working with Tests (tests.mk)
test: run-tests
test_debug: run-test-debug
cov: run-cov 

# Type Checking (typing.mk)
check: run-check

# Formatting the Code (format.mk)
format: run-format
format_tests: run-format-tests

# Code Health (stats.mk)
stats_size: size # Calculate the code size.
stats_scan: scan # Check for antipatterns and measure complexity.

# Generate code documentation (doc.mk)
doc: build-docs

# Debugging (debugging.mk)
debug: run-pudb

# Release (build.mk)
build: build-wheel # Create a distributable wheel.

# Profiling (profile.mk)
profile_flame_graph: flame         # Create a flame graph of use actions.
profile_top: top                   # Display a running list of the top most expensive functions while the app is running.
profile_function: profile-function # Profile any functions marked with @profile.
profile_test: profile-test         # Profile a specific unit test.

# Benchmarking (benchmark.mk)
benchmark: run-benchmarks                   # Run all benchmark tests.
benchmark_this: run-benchmark-this # Run a benchmark specified with BENCHMARK_THIS
benchmark_boxplots: run-benchmark-boxplots # Generate the benchmarks as boxplots.
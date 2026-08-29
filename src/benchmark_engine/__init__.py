"""Benchmark Engine Deep Dive: evaluates qualified models against scenario test cases."""

from benchmark_engine.agents import BenchmarkModelRoster
from benchmark_engine.engine import run_benchmark_deep_dive
from benchmark_engine.schema import BenchmarkResult, TestCase
from benchmark_engine.test_case_loader import (
    load_test_cases,
    parse_test_case_file,
    select_test_case_file,
)

__all__ = [
    "BenchmarkModelRoster",
    "BenchmarkResult",
    "TestCase",
    "load_test_cases",
    "parse_test_case_file",
    "run_benchmark_deep_dive",
    "select_test_case_file",
]

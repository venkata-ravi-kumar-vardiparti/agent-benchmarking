"""Data model for the Benchmark Engine Deep Dive.

The Benchmark Engine runs after Model Qualification: it takes the list of
qualified models and evaluates each of them against the test cases for the
scenario's industry and use case.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TestCase:
    """A single test question and its expected (reference) answer."""

    case_id: str
    title: str
    question: str
    expected_answer: str


@dataclass
class BenchmarkResult:
    """The outcome of running one qualified model against one test case."""

    model_name: str
    test_question: str
    original_test_response: str
    model_response: str

    def to_dict(self) -> dict:
        return {
            "model_name": self.model_name,
            "test_question": self.test_question,
            "original_test_response": self.original_test_response,
            "model_response": self.model_response,
        }

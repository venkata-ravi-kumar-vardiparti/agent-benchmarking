"""Loads test case markdown files from `src/test_cases/` and selects the file
that best matches a scenario's industry and use case."""

from __future__ import annotations

import re
from pathlib import Path

from benchmark_engine.schema import TestCase

TEST_CASES_DIR = Path(__file__).resolve().parents[1] / "test_cases"

_METADATA_PATTERN = re.compile(r"^\*\*(?P<key>[^:*]+):\*\*\s*(?P<value>.+?)\s*$")
_CASE_PATTERN = re.compile(
    r"^##\s*Test Case\s+(?P<id>[\w-]+):\s*(?P<title>[^\n]*)\n+"
    r"\*\*Question:\*\*\s*(?P<question>.*?)\n+"
    r"\*\*Expected Answer:\*\*\s*(?P<answer>.*?)(?=\n+---|\Z)",
    re.DOTALL | re.MULTILINE,
)


def parse_test_case_file(path: Path) -> tuple[str, str, list[TestCase]]:
    """Parse a test case markdown file into (industry, use_case, test_cases)."""
    text = path.read_text(encoding="utf-8")

    industry = ""
    use_case = ""
    for line in text.splitlines():
        match = _METADATA_PATTERN.match(line.strip())
        if not match:
            continue
        key = match.group("key").strip().lower()
        if key == "industry":
            industry = match.group("value").strip()
        elif key == "use case":
            use_case = match.group("value").strip()

    test_cases = [
        TestCase(
            case_id=match.group("id").strip(),
            title=match.group("title").strip(),
            question=" ".join(match.group("question").split()),
            expected_answer=" ".join(match.group("answer").split()),
        )
        for match in _CASE_PATTERN.finditer(text)
    ]

    return industry, use_case, test_cases


def select_test_case_file(
    industry: str,
    use_case: str,
    test_cases_dir: Path = TEST_CASES_DIR,
) -> Path:
    """Pick the markdown file whose industry/use case best matches the scenario.

    Industry match is the primary signal; overlapping use-case keywords break ties.
    """
    candidates = sorted(test_cases_dir.glob("*.md"))
    if not candidates:
        raise FileNotFoundError(f"No test case files found in {test_cases_dir}")

    use_case_words = set(re.findall(r"\w+", use_case.lower()))

    def score(path: Path) -> tuple[int, int]:
        file_industry, file_use_case, _ = parse_test_case_file(path)
        industry_match = int(file_industry.strip().lower() == industry.strip().lower())
        file_use_case_words = set(re.findall(r"\w+", file_use_case.lower()))
        overlap = len(use_case_words & file_use_case_words)
        return (industry_match, overlap)

    return max(candidates, key=score)


def load_test_cases(path: Path) -> list[TestCase]:
    """Load just the test cases from a markdown file (no metadata)."""
    _, _, test_cases = parse_test_case_file(path)
    return test_cases

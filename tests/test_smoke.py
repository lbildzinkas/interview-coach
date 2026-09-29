"""Smoke test: the package is installed and importable."""

import interview_coach


def test_package_imports() -> None:
    assert interview_coach.__name__ == "interview_coach"

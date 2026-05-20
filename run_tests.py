"""Run integration tests for the Lr-1-parser rule language."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_test(test_dir: Path, main_path: Path) -> bool:
    """Run one test directory and compare stdout with expected output."""

    rules_path = test_dir / "rules.txt"
    state_path = test_dir / "state.txt"
    expected_path = test_dir / "expected.txt"

    completed = subprocess.run(
        [sys.executable, str(main_path), str(rules_path), str(state_path)],
        capture_output=True,
        text=True,
    )

    expected = expected_path.read_text(encoding="utf-8").strip()
    actual = completed.stdout.strip()

    if actual == expected:
        print(f"PASS {test_dir.name}")
        return True

    print(f"FAIL {test_dir.name}")
    print("Expected output")
    print(expected)
    print("Actual output")
    print(actual)
    return False


def main() -> int:
    """Discover and run all complete test cases in the tests directory."""

    project_dir = Path(__file__).resolve().parent
    tests_dir = project_dir / "tests"
    main_path = project_dir / "main.py"

    test_dirs = [
        path
        for path in sorted(tests_dir.iterdir())
        if path.is_dir()
        and (path / "rules.txt").is_file()
        and (path / "state.txt").is_file()
        and (path / "expected.txt").is_file()
    ]

    passed = 0
    for test_dir in test_dirs:
        if run_test(test_dir, main_path):
            passed += 1

    total = len(test_dirs)
    print(f"Passed {passed}/{total} tests.")

    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())

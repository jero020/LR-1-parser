"""Command-line entry point for the PC monitoring rule language."""

from __future__ import annotations

import sys
from pathlib import Path

from interpreter import Interpreter
from parser import parse_program
from static_analysis import StaticAnalyzer


def parse_state(text: str) -> tuple[dict[str, int], set[str]]:
    """Parse initial variables and active facts from state text.

    Blank lines are ignored. Lines containing ``=`` are treated as integer
    variable assignments, and all other non-empty lines are treated as active
    facts.
    """

    variables: dict[str, int] = {}
    facts: set[str] = set()

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if "=" in line:
            identifier, value = line.split("=", 1)
            variables[identifier.strip()] = int(value.strip())
        else:
            facts.add(line)

    return variables, facts


def print_execution_output(derived_facts: set[str]) -> None:
    """Print derived facts in the canonical output format."""

    if not derived_facts:
        print("(no output)")
        return

    for fact in sorted(derived_facts):
        print(fact)


def main(argv: list[str] | None = None) -> int:
    """Run the parser, interpreter, and static analyzer from CLI arguments."""

    args = sys.argv[1:] if argv is None else argv
    if len(args) not in (1, 2):
        print("Usage: python main.py <rules_file> [state_file]", file=sys.stderr)
        return 1

    rules_text = Path(args[0]).read_text(encoding="utf-8")
    state_text = Path(args[1]).read_text(encoding="utf-8") if len(args) == 2 else ""

    program = parse_program(rules_text)
    variables, facts = parse_state(state_text)

    interpreter = Interpreter(program, variables, facts)
    derived_facts = interpreter.run()

    analyzer = StaticAnalyzer(program, interpreter.applied_rules)
    messages = analyzer.analyze()

    print_execution_output(derived_facts)
    for message in messages:
        print(message)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

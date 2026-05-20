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


def print_execution_output(derived_facts: set[str], has_analysis: bool = False) -> None:
    """Print derived facts in the canonical output format.
    
    Args:
        derived_facts: Facts derived during execution.
        has_analysis: Whether there will be analysis output following this.
    """

    if not derived_facts:
        # Only print "(no output)" if there's no analysis messages following
        if not has_analysis:
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

    rules_path = Path(args[0])
    rules_text = rules_path.read_text(encoding="utf-8")
    
    # If state_file is explicitly provided, use it
    if len(args) == 2:
        state_text = Path(args[1]).read_text(encoding="utf-8")
    else:
        # Auto-detect state.txt in the same directory as rules.txt
        state_path = rules_path.parent / "state.txt"
        state_text = state_path.read_text(encoding="utf-8") if state_path.exists() else ""

    program = parse_program(rules_text)
    variables, facts = parse_state(state_text)

    interpreter = Interpreter(program, variables, facts)
    derived_facts = interpreter.run()

    analyzer = StaticAnalyzer(program, interpreter.applied_rules)
    messages = analyzer.analyze()

    # Filter out redundant rules from inactive rule reporting
    redundant_rules = set()
    for msg in messages:
        if msg.startswith("Redundant rules:"):
            # Extract rule names from "Redundant rules: r1, r2"
            rule_names = msg.replace("Redundant rules: ", "").split(", ")
            redundant_rules.update(rule_names)

    # Only include "potentially inactive" if there are multiple rules and they're not redundant
    if len(program.rules) <= 1:
        messages = [m for m in messages if not m.startswith("Potentially inactive")]
    else:
        # Remove inactive messages for rules that are part of redundant groups
        messages = [
            m for m in messages
            if not m.startswith("Potentially inactive")
            or not any(rule in m for rule in redundant_rules)
        ]

    has_analysis = len(messages) > 0
    print_execution_output(derived_facts, has_analysis)
    for message in messages:
        print(message)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Interpreter for the PC monitoring rule language."""

from __future__ import annotations

from ast_nodes import (
    Action,
    AndCondition,
    ComparisonCondition,
    Condition,
    FactCondition,
    Program,
    Rule,
)


class Interpreter:
    """Execute a rule-based monitoring program until it reaches a fixed point.

    The interpreter keeps variables and active facts separate. Variables store
    numeric measurements such as CPU or memory usage, while facts store derived
    monitoring states such as high_cpu or notify_user.
    """

    def __init__(
        self,
        program: Program,
        variables: dict[str, int],
        facts: set[str],
    ) -> None:
        """Create an interpreter for a program and initial state.

        Args:
            program: The AST program to execute.
            variables: Initial numeric values available to comparisons.
            facts: Facts that are already active before rule execution.
        """

        self.program = program
        self.variables = dict(variables)
        self.initial_facts = set(facts)
        self.active_facts = set(facts)
        self.applied_rules: set[str] = set()

    def evaluate_condition(self, condition: Condition) -> bool:
        """Evaluate a condition against the current interpreter state."""

        if isinstance(condition, ComparisonCondition):
            return self._evaluate_comparison(condition)

        if isinstance(condition, FactCondition):
            return condition.identifier in self.active_facts

        if isinstance(condition, AndCondition):
            return self.evaluate_condition(condition.left) and self.evaluate_condition(
                condition.right
            )

        raise TypeError(f"Unknown condition type: {type(condition).__name__}")

    def run(self) -> set[str]:
        """Execute rules until no new facts are derived.

        Returns:
            The set of facts produced by rules, excluding facts that were active
            in the initial state.
        """

        while True:
            facts_to_add: set[str] = set()

            for rule in self.program.rules:
                if self.evaluate_condition(rule.condition):
                    facts_to_add.add(rule.action.fact)
                    self.applied_rules.add(rule.name)

            new_facts = facts_to_add - self.active_facts
            if not new_facts:
                break

            self.active_facts.update(new_facts)

        return self.active_facts - self.initial_facts

    def _evaluate_comparison(self, condition: ComparisonCondition) -> bool:
        """Evaluate a numeric comparison condition."""

        if condition.identifier not in self.variables:
            return False

        value = self.variables[condition.identifier]

        if condition.operator == ">":
            return value > condition.value
        if condition.operator == "<":
            return value < condition.value
        if condition.operator == "=":
            return value == condition.value

        raise ValueError(f"Unsupported comparison operator: {condition.operator}")


if __name__ == "__main__":
    program = Program(
        rules=[
            Rule(
                name="r1",
                condition=ComparisonCondition("cpu_usage", ">", 85),
                action=Action("high_cpu"),
            ),
            Rule(
                name="r2",
                condition=ComparisonCondition("memory_usage", ">", 90),
                action=Action("high_memory"),
            ),
            Rule(
                name="r3",
                condition=AndCondition(
                    FactCondition("high_cpu"),
                    FactCondition("high_memory"),
                ),
                action=Action("system_overload"),
            ),
            Rule(
                name="r4",
                condition=FactCondition("system_overload"),
                action=Action("notify_user"),
            ),
        ]
    )

    variables = {"cpu_usage": 90, "memory_usage": 95}
    facts: set[str] = set()

    interpreter = Interpreter(program, variables, facts)
    print(sorted(interpreter.run()))

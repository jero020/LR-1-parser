"""Abstract Syntax Tree node definitions for the PC monitoring rule language."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Program:
    """A complete program made of monitoring rules.

    Each rule describes a condition to check and the fact to assert when that
    condition is satisfied.
    """

    rules: list[Rule]


@dataclass(frozen=True)
class Rule:
    """A named monitoring rule with a condition and an action.

    Example:
        rule r1:
        if cpu_usage > 85 then high_cpu

        Rule(
            name="r1",
            condition=ComparisonCondition("cpu_usage", ">", 85),
            action=Action("high_cpu"),
        )
    """

    name: str
    condition: Condition
    action: Action


@dataclass(frozen=True)
class Action:
    """The fact produced when a rule condition is satisfied."""

    fact: str


@dataclass(frozen=True)
class Condition:
    """Base class for all rule conditions."""


@dataclass(frozen=True)
class ComparisonCondition(Condition):
    """A numeric comparison against a monitored value.

    Example: cpu_usage > 85
    """

    identifier: str
    operator: str
    value: int


@dataclass(frozen=True)
class FactCondition(Condition):
    """A condition that checks whether a named fact is currently known.

    Example: high_cpu
    """

    identifier: str


@dataclass(frozen=True)
class AndCondition(Condition):
    """A condition that requires both child conditions to be true.

    Example:
        rule r2:
        if high_cpu AND high_memory then system_overload

        Rule(
            name="r2",
            condition=AndCondition(
                FactCondition("high_cpu"),
                FactCondition("high_memory"),
            ),
            action=Action("system_overload"),
        )
    """

    left: Condition
    right: Condition


__all__ = [
    "Program",
    "Rule",
    "Action",
    "Condition",
    "ComparisonCondition",
    "FactCondition",
    "AndCondition",
]

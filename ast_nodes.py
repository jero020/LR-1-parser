"""Abstract Syntax Tree node definitions for the PC monitoring rule language."""

from __future__ import annotations

from dataclasses import dataclass


# Nodo raiz del AST: agrupa todas las reglas parseadas desde el archivo.
@dataclass(frozen=True)
class Program:
    """A complete program made of monitoring rules.

    Each rule describes a condition to check and the fact to assert when that
    condition is satisfied.
    """

    # Lista ordenada de reglas tal como aparecen en el programa fuente.
    rules: list[Rule]


# Nodo que representa una regla completa con nombre, condicion y accion.
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

    # Identificador usado para reportes de ejecucion y analisis.
    name: str
    # Condicion que debe cumplirse para activar la accion.
    condition: Condition
    # Hecho producido cuando la condicion resulta verdadera.
    action: Action


# Nodo simple para la consecuencia de una regla: activar un hecho.
@dataclass(frozen=True)
class Action:
    """The fact produced when a rule condition is satisfied."""

    # Nombre del hecho que se agrega al conjunto de hechos activos.
    fact: str


# Clase base de condiciones. Sirve para tipar funciones que aceptan cualquier
# clase concreta de condicion.
@dataclass(frozen=True)
class Condition:
    """Base class for all rule conditions."""


# Condicion de comparacion numerica: consulta una variable del estado inicial.
@dataclass(frozen=True)
class ComparisonCondition(Condition):
    """A numeric comparison against a monitored value.

    Example: cpu_usage > 85
    """

    # Variable a buscar en el diccionario de variables del interprete.
    identifier: str
    # Operador relacional permitido: ">", "<" o "=".
    operator: str
    # Valor entero contra el que se compara la variable.
    value: int


# Condicion booleana basada en hechos: pregunta si un hecho ya esta activo.
@dataclass(frozen=True)
class FactCondition(Condition):
    """A condition that checks whether a named fact is currently known.

    Example: high_cpu
    """

    # Nombre del hecho que debe estar en active_facts.
    identifier: str


# Condicion compuesta: ambas ramas deben ser verdaderas para cumplir la regla.
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

    # Rama izquierda de la conjuncion.
    left: Condition
    # Rama derecha de la conjuncion.
    right: Condition


# Define la API publica del modulo para imports explicitos o comodin.
__all__ = [
    "Program",
    "Rule",
    "Action",
    "Condition",
    "ComparisonCondition",
    "FactCondition",
    "AndCondition",
]

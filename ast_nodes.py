"""Abstract Syntax Tree node definitions for the PC monitoring rule language."""

from __future__ import annotations

from dataclasses import dataclass


# Nodo raiz del AST: agrupa todas las reglas parseadas desde el archivo.
@dataclass(frozen=True)
class Program:
    """Representa el programa completo ya parseado.

    Dentro guarda todas las reglas que el interprete va a evaluar.
    """

    # Lista ordenada de reglas tal como aparecen en el programa fuente.
    rules: list[Rule]


# Nodo que representa una regla completa con nombre, condicion y accion.
@dataclass(frozen=True)
class Rule:
    """Representa una regla del lenguaje.

    Una regla tiene nombre, una condicion que se evalua y una accion que se
    ejecuta cuando esa condicion es verdadera.
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
    """Representa el hecho que se activa cuando una regla se cumple."""

    # Nombre del hecho que se agrega al conjunto de hechos activos.
    fact: str


# Clase base de condiciones. Sirve para tipar funciones que aceptan cualquier
# clase concreta de condicion.
@dataclass(frozen=True)
class Condition:
    """Clase base para cualquier tipo de condicion del lenguaje."""


# Condicion de comparacion numerica: consulta una variable del estado inicial.
@dataclass(frozen=True)
class ComparisonCondition(Condition):
    """Representa una comparacion numerica.

    Por ejemplo: ``temp > 30`` o ``humidity < 50``.
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
    """Representa una pregunta sobre un hecho activo.

    Por ejemplo: ``alert`` significa "la condicion es verdadera si alert ya
    esta en el conjunto de hechos activos".
    """

    # Nombre del hecho que debe estar en active_facts.
    identifier: str


# Condicion compuesta: ambas ramas deben ser verdaderas para cumplir la regla.
@dataclass(frozen=True)
class AndCondition(Condition):
    """Representa dos condiciones unidas por ``AND``.

    Solo es verdadera cuando la condicion izquierda y la condicion derecha son
    verdaderas al mismo tiempo.
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

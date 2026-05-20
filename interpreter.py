"""Interpreter for the PC monitoring rule language."""

from __future__ import annotations

# El interprete no lee texto: recibe el AST ya construido y evalua sus nodos.
from ast_nodes import (
    Action,
    AndCondition,
    ComparisonCondition,
    Condition,
    FactCondition,
    Program,
    Rule,
)


# Ejecuta las reglas repetidamente hasta que no pueda derivar hechos nuevos.
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

        # Guarda el programa y copia el estado inicial para evitar modificar
        # las estructuras recibidas desde afuera.
        self.program = program
        self.variables = dict(variables)
        self.initial_facts = set(facts)
        self.active_facts = set(facts)
        # Registro de reglas que llegaron a dispararse durante la ejecucion.
        self.applied_rules: set[str] = set()

    def evaluate_condition(self, condition: Condition) -> bool:
        """Evaluate a condition against the current interpreter state."""

        # Comparaciones numericas se delegan a un metodo especializado.
        if isinstance(condition, ComparisonCondition):
            return self._evaluate_comparison(condition)

        # Una condicion de hecho es verdadera si el hecho ya esta activo.
        if isinstance(condition, FactCondition):
            return condition.identifier in self.active_facts

        # AND evalua recursivamente ambas ramas y exige que las dos sean true.
        if isinstance(condition, AndCondition):
            return self.evaluate_condition(condition.left) and self.evaluate_condition(
                condition.right
            )

        # Defensa para detectar nuevos tipos de condicion no soportados.
        raise TypeError(f"Unknown condition type: {type(condition).__name__}")

    def run(self) -> set[str]:
        """Execute rules until no new facts are derived.

        Returns:
            The set of facts produced by rules, excluding facts that were active
            in the initial state.
        """

        # Bucle de punto fijo: cada vuelta evalua todas las reglas con el
        # estado actual y agrega hechos nuevos al final de la iteracion.
        while True:
            facts_to_add: set[str] = set()

            # Se revisan todas las reglas antes de actualizar active_facts para
            # mantener una ejecucion determinista por rondas.
            for rule in self.program.rules:
                if self.evaluate_condition(rule.condition):
                    facts_to_add.add(rule.action.fact)
                    self.applied_rules.add(rule.name)

            # Solo interesan los hechos que aun no estaban activos.
            new_facts = facts_to_add - self.active_facts
            if not new_facts:
                break

            # Los hechos nuevos quedan disponibles para la siguiente ronda.
            self.active_facts.update(new_facts)

        # Devuelve solo hechos derivados, no los que venian en el estado inicial.
        return self.active_facts - self.initial_facts

    def _evaluate_comparison(self, condition: ComparisonCondition) -> bool:
        """Evaluate a numeric comparison condition."""

        # Si la variable no existe en el estado, la comparacion no se cumple.
        if condition.identifier not in self.variables:
            return False

        value = self.variables[condition.identifier]

        # Aplica el operador guardado en el AST contra el valor esperado.
        if condition.operator == ">":
            return value > condition.value
        if condition.operator == "<":
            return value < condition.value
        if condition.operator == "=":
            return value == condition.value

        # El parser solo deberia producir operadores validos; esto protege si
        # se construye un AST manualmente con un operador no soportado.
        raise ValueError(f"Unsupported comparison operator: {condition.operator}")


if __name__ == "__main__":
    # Prueba manual: construye el AST en codigo y verifica encadenamiento de
    # reglas hasta derivar notify_user.
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

    # Estado inicial con variables numericas y sin hechos activos.
    variables = {"cpu_usage": 90, "memory_usage": 95}
    facts: set[str] = set()

    interpreter = Interpreter(program, variables, facts)
    print(sorted(interpreter.run()))

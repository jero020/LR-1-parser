"""Command-line entry point for the PC monitoring rule language."""

from __future__ import annotations

import sys
from pathlib import Path

# Se importan los tres pasos centrales del programa: interpretar reglas,
# construir el AST desde texto y revisar advertencias estaticas.
from interpreter import Interpreter
from parser import parse_program
from static_analysis import StaticAnalyzer


def parse_state(text: str) -> tuple[dict[str, int], set[str]]:
    """Lee el archivo de estado inicial y lo divide en dos grupos.

    Las lineas como ``temp = 35`` se guardan como variables numericas porque
    sirven para comparaciones. Las lineas como ``alert`` se guardan como hechos
    activos porque representan cosas que ya son verdaderas antes de ejecutar
    las reglas.
    """

    variables: dict[str, int] = {}
    facts: set[str] = set()

    # Recorre el archivo de estado linea por linea y separa asignaciones
    # numericas de hechos booleanos activos.
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        # Una linea con "=" representa una variable numerica usada por las
        # comparaciones de las reglas, por ejemplo: temp = 35.
        if "=" in line:
            identifier, value = line.split("=", 1)
            variables[identifier.strip()] = int(value.strip())
        else:
            # Una linea sin "=" representa un hecho que ya esta activo antes
            # de ejecutar el sistema de reglas.
            facts.add(line)

    return variables, facts


def print_execution_output(derived_facts: set[str], has_analysis: bool = False) -> None:
    """Imprime el resultado principal del programa.

    Muestra los hechos nuevos que se derivaron durante la ejecucion. Si no hay
    hechos nuevos, imprime ``(no output)`` solamente cuando tampoco hay mensajes
    de analisis que mostrar.
    """

    # Si no hay hechos derivados, solo se imprime el marcador especial cuando
    # tampoco existen mensajes de analisis que mostrar despues.
    if not derived_facts:
        if not has_analysis:
            print("(no output)")
        return

    # Los hechos se ordenan para que la salida sea determinista e igual en
    # todas las ejecuciones.
    for fact in sorted(derived_facts):
        print(fact)


def main(argv: list[str] | None = None) -> int:
    """Coordina todo el programa desde la linea de comandos.

    Lee los archivos de entrada, convierte las reglas en AST, ejecuta el
    interprete, corre el analisis estatico y finalmente imprime la salida en el
    orden esperado.
    """

    # Toma argumentos reales de consola, salvo que una prueba pase una lista
    # explicita para ejecutar main de forma controlada.
    args = sys.argv[1:] if argv is None else argv
    if len(args) not in (1, 2):
        print("Usage: python main.py <rules_file> [state_file]", file=sys.stderr)
        return 1

    # Lee el archivo obligatorio de reglas; este texto sera tokenizado y
    # parseado por los modulos lexer/parser.
    rules_path = Path(args[0])
    rules_text = rules_path.read_text(encoding="utf-8")
    
    # Si se pasa un archivo de estado, se usa directamente.
    if len(args) == 2:
        state_text = Path(args[1]).read_text(encoding="utf-8")
    else:
        # Si no se pasa, intenta autodetectar state.txt junto a rules.txt.
        state_path = rules_path.parent / "state.txt"
        state_text = state_path.read_text(encoding="utf-8") if state_path.exists() else ""

    # Convierte las reglas a AST y el estado inicial a estructuras Python
    # separadas: variables numericas y hechos activos.
    program = parse_program(rules_text)
    variables, facts = parse_state(state_text)

    # Ejecuta las reglas hasta alcanzar punto fijo, es decir, hasta que una
    # iteracion completa no derive hechos nuevos.
    interpreter = Interpreter(program, variables, facts)
    derived_facts = interpreter.run()

    # Analiza el AST y las reglas aplicadas para detectar conflictos,
    # redundancias y reglas potencialmente inactivas.
    analyzer = StaticAnalyzer(program, interpreter.applied_rules)
    messages = analyzer.analyze()

    # Extrae reglas redundantes para no reportarlas tambien como inactivas;
    # asi la salida coincide con el formato esperado por las pruebas.
    redundant_rules = set()
    for msg in messages:
        if msg.startswith("Redundant rules:"):
            rule_names = msg.replace("Redundant rules: ", "").split(", ")
            redundant_rules.update(rule_names)

    # Ajusta los mensajes de inactividad: se omiten para programas de una sola
    # regla y tambien para reglas que ya fueron marcadas como redundantes.
    if len(program.rules) <= 1:
        messages = [m for m in messages if not m.startswith("Potentially inactive")]
    else:
        messages = [
            m for m in messages
            if not m.startswith("Potentially inactive")
            or not any(rule in m for rule in redundant_rules)
        ]

    # Primero imprime hechos derivados y luego advertencias de analisis, que es
    # el contrato de salida usado por los casos de prueba.
    has_analysis = len(messages) > 0
    print_execution_output(derived_facts, has_analysis)
    for message in messages:
        print(message)

    return 0


if __name__ == "__main__":
    # Permite ejecutar el archivo como script y devolver el codigo de salida
    # producido por main al sistema operativo.
    raise SystemExit(main())

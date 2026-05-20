"""Run integration tests for the Lr-1-parser rule language."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


# Ejecuta un caso de prueba completo y compara la salida real con expected.txt.
def run_test(test_dir: Path, main_path: Path) -> bool:
    """Ejecuta una carpeta de prueba y verifica si la salida coincide.

    Cada caso tiene ``rules.txt``, ``state.txt`` y ``expected.txt``. La funcion
    corre el programa real con esos archivos y compara lo que imprimio contra
    la salida esperada.
    """

    # Cada carpeta de prueba debe contener reglas, estado inicial y salida
    # esperada con nombres fijos.
    rules_path = test_dir / "rules.txt"
    state_path = test_dir / "state.txt"
    expected_path = test_dir / "expected.txt"

    # Lanza main.py en un proceso separado para probar el programa como lo
    # usaria una persona desde la linea de comandos.
    completed = subprocess.run(
        [sys.executable, str(main_path), str(rules_path), str(state_path)],
        capture_output=True,
        text=True,
    )

    # Normaliza espacios al inicio/final para comparar solo el contenido.
    expected = expected_path.read_text(encoding="utf-8").strip()
    actual = completed.stdout.strip()

    # Si coincide, reporta PASS y devuelve True al contador general.
    if actual == expected:
        print(f"PASS {test_dir.name}")
        return True

    # Si falla, muestra expected vs actual para diagnosticar rapidamente.
    print(f"FAIL {test_dir.name}")
    print("Expected output")
    print(expected)
    print("Actual output")
    print(actual)
    return False


def main() -> int:
    """Busca todos los casos de prueba completos y los ejecuta.

    Al final imprime cuantos pasaron y devuelve codigo 0 si todos fueron
    correctos, o codigo 1 si alguno fallo.
    """

    # Calcula rutas relativas al archivo actual para poder ejecutar las pruebas
    # desde cualquier directorio de trabajo.
    project_dir = Path(__file__).resolve().parent
    tests_dir = project_dir / "tests"
    main_path = project_dir / "main.py"

    # Descubre solamente carpetas que tengan los tres archivos requeridos.
    test_dirs = [
        path
        for path in sorted(tests_dir.iterdir())
        if path.is_dir()
        and (path / "rules.txt").is_file()
        and (path / "state.txt").is_file()
        and (path / "expected.txt").is_file()
    ]

    # Ejecuta cada caso y cuenta cuantos pasaron.
    passed = 0
    for test_dir in test_dirs:
        if run_test(test_dir, main_path):
            passed += 1

    # Imprime resumen final y usa codigo de salida 0 solo si todo paso.
    total = len(test_dirs)
    print(f"Passed {passed}/{total} tests.")

    return 0 if passed == total else 1


if __name__ == "__main__":
    # Permite llamar el runner directamente con python run_tests.py.
    raise SystemExit(main())

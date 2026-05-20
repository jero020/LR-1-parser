"""LR(1)-compatible parser for the rule-based language.

This parser implements the grammar:
    Program -> RuleList
    RuleList -> Rule RuleList | epsilon
    Rule -> rule id : if Cond then Action
    Cond -> Cond AND Cond | Atom
    Atom -> id RelOp value | id
    RelOp -> > | < | =
    Action -> id

The implementation uses recursive descent, which is compatible with LR(1).
"""

from __future__ import annotations

# Importa las clases del AST que el parser va construyendo conforme reconoce
# reglas, condiciones y acciones.
from ast_nodes import (
    Action,
    AndCondition,
    ComparisonCondition,
    Condition,
    FactCondition,
    Program,
    Rule,
)
from lexer import Token, TokenType, tokenize


# Error propio del parser: separa fallos sintacticos de fallos lexicos.
class ParseError(Exception):
    """Error que aparece cuando los tokens no siguen la gramatica esperada."""

    pass


# El parser consume la lista de tokens de izquierda a derecha y produce un AST.
class Parser:
    """Convierte una lista de tokens en un arbol de sintaxis abstracta."""

    def __init__(self, tokens: list[Token]) -> None:
        """Prepara el parser para leer tokens desde el primero hasta EOF.

        La posicion ``pos`` marca cual token se esta revisando en este momento.
        """
        # pos apunta al token actual dentro del flujo; no se copian tokens.
        self.tokens = tokens
        self.pos = 0

    def error(self, message: str) -> None:
        """Lanza un error sintactico indicando donde se rompio la gramatica.

        Se usa cuando el parser esperaba un tipo de token y encontro otro.
        """
        # Usa el token actual para ubicar el error y mostrar que se esperaba.
        token = self.current_token()
        raise ParseError(
            f"Parse error at line {token.line}, column {token.column}: {message}. "
            f"Got {token.type.name} ({token.lexeme!r})"
        )

    def current_token(self) -> Token:
        """Devuelve el token actual sin mover la posicion del parser."""
        # Devuelve EOF si se intenta leer mas alla, evitando errores de indice.
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def peek(self, offset: int = 0) -> Token:
        """Mira un token futuro sin consumir ningun token.

        Es util cuando el parser necesita decidir que camino tomar segun lo que
        viene despues.
        """
        # Permite mirar tokens futuros para tomar decisiones sintacticas.
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]

    def advance(self) -> Token:
        """Consume el token actual y avanza al siguiente.

        Si ya esta en EOF, se queda ahi porque EOF funciona como marcador final.
        """
        # Consume el token actual, salvo EOF, que se mantiene como centinela.
        token = self.current_token()
        if token.type != TokenType.EOF:
            self.pos += 1
        return token

    def expect(self, token_type: TokenType) -> Token:
        """Exige que el token actual sea de cierto tipo.

        Si coincide, lo consume y lo devuelve. Si no coincide, detiene el parseo
        con un error claro.
        """
        # Verifica que la gramatica pida exactamente el token actual.
        token = self.current_token()
        if token.type != token_type:
            self.error(f"Expected {token_type.name}, got {token.type.name}")
        return self.advance()

    def match(self, *token_types: TokenType) -> bool:
        """Pregunta si el token actual coincide con alguno de los tipos dados."""
        # Consulta rapida para producciones opcionales o alternativas.
        return self.current_token().type in token_types

    def parse(self) -> Program:
        """Parsea el programa completo.

        Primero lee todas las reglas y luego verifica que no haya tokens
        sobrantes despues del final esperado.
        """
        # La raiz de la gramatica es una lista de reglas seguida por EOF.
        rules = self.parse_rule_list()
        self.expect(TokenType.EOF)
        return Program(rules=rules)

    def parse_rule_list(self) -> list[Rule]:
        """Lee todas las reglas que aparezcan una despues de otra.

        Se detiene cuando el siguiente token ya no es ``rule``. Si no hay
        ninguna regla, devuelve una lista vacia.
        """
        # Lee reglas consecutivas hasta que ya no aparezca la palabra "rule".
        rules: list[Rule] = []

        while self.match(TokenType.RULE):
            rules.append(self.parse_rule())

        return rules

    def parse_rule(self) -> Rule:
        """Lee una regla completa y la convierte en un nodo ``Rule``.

        La forma esperada es: ``rule nombre: if condicion then accion``.
        """
        # Estructura obligatoria de cada regla: rule <id>: if <cond> then <id>.
        self.expect(TokenType.RULE)

        # Nombre de la regla, usado despues por reportes y analisis estatico.
        name_token = self.expect(TokenType.ID)
        rule_name = name_token.lexeme

        # Dos puntos que separan encabezado y cuerpo de la regla.
        self.expect(TokenType.COLON)

        # Palabra clave que inicia la condicion.
        self.expect(TokenType.IF)

        # Subarbol que representa comparaciones, hechos o conjunciones AND.
        condition = self.parse_condition()

        # Palabra clave que separa condicion y accion.
        self.expect(TokenType.THEN)

        # Accion final: el hecho que se activara si la condicion es verdadera.
        action = self.parse_action()

        return Rule(name=rule_name, condition=condition, action=action)

    def parse_condition(self) -> Condition:
        """Lee una condicion completa.

        Puede ser una condicion simple o varias condiciones unidas por ``AND``.
        Cuando hay varios ``AND``, arma un arbol de condiciones encadenadas.
        """
        # Primero lee un atomo; luego encadena todos los AND encontrados para
        # formar un arbol binario de condiciones.
        left = self.parse_atom()

        while self.match(TokenType.AND):
            self.advance()
            right = self.parse_atom()
            left = AndCondition(left, right)

        return left

    def parse_atom(self) -> Condition:
        """Lee la parte mas pequena de una condicion.

        Si encuentra ``id operador numero``, crea una comparacion. Si encuentra
        solo ``id``, crea una condicion que pregunta si ese hecho esta activo.
        """
        # Todo atomo inicia con un identificador: variable para comparacion o
        # nombre de hecho para condicion booleana.
        if not self.match(TokenType.ID):
            self.error("Expected identifier in condition")

        identifier_token = self.advance()
        identifier = identifier_token.lexeme

        # Si despues del identificador viene un operador relacional, el atomo
        # es una comparacion numerica.
        if self.match(TokenType.GT, TokenType.LT, TokenType.EQ):
            operator_token = self.advance()
            operator = operator_token.lexeme

            # La comparacion siempre termina con un valor entero.
            value_token = self.expect(TokenType.VALUE)
            value = int(value_token.lexeme)

            return ComparisonCondition(
                identifier=identifier, operator=operator, value=value
            )

        # Si no hay operador, el identificador se interpreta como hecho
        # activo/inactivo dentro del interprete.
        return FactCondition(identifier=identifier)

    def parse_action(self) -> Action:
        """Lee la accion de una regla.

        En este lenguaje, una accion solo significa activar un hecho con nombre.
        """
        # La accion solo puede activar un hecho identificado por un ID.
        identifier_token = self.expect(TokenType.ID)
        return Action(fact=identifier_token.lexeme)


def parse_program(text: str) -> Program:
    """Convierte texto de reglas directamente en un ``Program``.

    Es el acceso principal del modulo: primero llama al lexer para crear tokens
    y luego usa ``Parser`` para construir el AST.
    """
    # Fase 1: convertir texto a tokens. Fase 2: consumir tokens y construir AST.
    tokens = tokenize(text)
    parser = Parser(tokens)
    return parser.parse()


if __name__ == "__main__":
    # Prueba manual rapida: parsea dos reglas y muestra sus nombres.
    code = """rule r1:
if temp > 30 then alert

rule r2:
if alert AND active then notify
"""

    program = parse_program(code)
    print(f"Parsed {len(program.rules)} rules")
    for rule in program.rules:
        print(f"  Rule: {rule.name}")

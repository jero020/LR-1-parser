"""Lexical analyzer (tokenizer) for the rule-based language."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


# Este enum define el vocabulario que reconoce el lexer. Cada token producido
# por el analizador lexico usa uno de estos tipos para que el parser no tenga
# que trabajar con caracteres sueltos.
class TokenType(Enum):
    """Lista todos los tipos de piezas que puede reconocer el lenguaje."""

    # Palabras reservadas del lenguaje de reglas.
    RULE = auto()
    IF = auto()
    THEN = auto()
    AND = auto()

    # Operadores y signos de puntuacion con significado sintactico.
    COLON = auto()  # :
    GT = auto()  # >
    LT = auto()  # <
    EQ = auto()  # =

    # Valores variables: identificadores definidos por el usuario y enteros.
    ID = auto()  # Identifiers
    VALUE = auto()  # Integer values

    # Marcadores especiales para cerrar la entrada o representar saltos.
    EOF = auto()
    NEWLINE = auto()


# Un Token conserva tanto el tipo como el texto original y su ubicacion. Esa
# ubicacion permite construir mensajes de error claros.
@dataclass
class Token:
    """Representa una pieza del texto ya reconocida por el lexer."""

    type: TokenType
    lexeme: str
    line: int
    column: int

    def __repr__(self) -> str:
        """Devuelve una version legible del token para depurar el programa."""
        # Representacion compacta para depurar la lista de tokens.
        return f"Token({self.type.name}, {self.lexeme!r}, {self.line}, {self.column})"


class Lexer:
    """Lee texto crudo de reglas y lo transforma en una lista de tokens."""

    # Tabla de palabras reservadas: si el texto leido coincide con una clave,
    # se genera su token especial; si no, se trata como identificador normal.
    KEYWORDS = {
        "rule": TokenType.RULE,
        "if": TokenType.IF,
        "then": TokenType.THEN,
        "AND": TokenType.AND,
    }

    def __init__(self, text: str) -> None:
        """Prepara el lexer para empezar a recorrer el texto desde el inicio.

        Guarda el texto completo y crea contadores para saber en que posicion,
        linea y columna se encuentra mientras avanza.
        """
        # Estado interno del recorrido: posicion absoluta, linea, columna y
        # lista acumulada de tokens encontrados.
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []

    def error(self, message: str) -> None:
        """Detiene el lexer cuando encuentra un caracter que no entiende.

        El mensaje incluye linea y columna para que sea facil ubicar el error
        dentro del archivo de reglas.
        """
        # Centraliza los errores lexicos para que todos incluyan ubicacion.
        raise SyntaxError(
            f"Lexical error at line {self.line}, column {self.column}: {message}"
        )

    def peek(self, offset: int = 0) -> str:
        """Mira un caracter sin avanzar la posicion actual.

        Sirve para decidir que hacer con el siguiente caracter antes de
        consumirlo. El parametro ``offset`` permite mirar un poco mas adelante.
        """
        # Mira hacia adelante sin mover la posicion; devuelve "\0" al final
        # para simplificar comparaciones en los bucles.
        pos = self.pos + offset
        if pos < len(self.text):
            return self.text[pos]
        return "\0"

    def advance(self) -> str:
        """Consume el caracter actual y mueve el cursor al siguiente.

        Tambien actualiza linea y columna, asi que el lexer siempre sabe donde
        esta parado dentro del texto.
        """
        # Consume el caracter actual y actualiza linea/columna para mantener
        # la posicion real del siguiente token.
        if self.pos >= len(self.text):
            return "\0"

        char = self.text[self.pos]
        self.pos += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def skip_whitespace(self) -> None:
        """Salta espacios y tabulaciones que no aportan significado.

        No salta cambios de linea porque esos se manejan aparte dentro del
        recorrido principal.
        """
        # Ignora espacios horizontales entre tokens; los saltos de linea se
        # manejan aparte dentro de tokenize.
        while self.peek() in (" ", "\t"):
            self.advance()

    def skip_newlines_and_whitespace(self) -> None:
        """Salta cualquier espacio, incluyendo cambios de linea.

        Es una funcion auxiliar general; el tokenizador principal normalmente
        maneja los saltos de linea de forma explicita.
        """
        # Utilidad para consumir cualquier espacio, aunque actualmente el
        # tokenizador principal decide los saltos de linea explicitamente.
        while self.peek() in (" ", "\t", "\n", "\r"):
            self.advance()

    def read_identifier(self) -> str:
        """Lee una palabra completa desde la posicion actual.

        Esa palabra puede terminar siendo una palabra reservada como ``rule`` o
        un identificador normal como ``temp`` o ``alert``.
        """
        # Un identificador puede contener letras, numeros y guion bajo; se lee
        # completo para luego decidir si es palabra reservada.
        start_pos = self.pos
        start_col = self.column

        while self.peek() and (self.peek().isalnum() or self.peek() == "_"):
            self.advance()

        return self.text[start_pos : self.pos]

    def read_number(self) -> str:
        """Lee un numero entero completo desde la posicion actual."""
        # Lee una secuencia continua de digitos que despues el parser convierte
        # a entero para las comparaciones.
        start_pos = self.pos

        while self.peek() and self.peek().isdigit():
            self.advance()

        return self.text[start_pos : self.pos]

    def add_token(self, token_type: TokenType, lexeme: str) -> None:
        """Crea un token nuevo y lo agrega a la lista de tokens encontrados."""
        # La columna inicial se reconstruye restando la longitud del lexema
        # porque la posicion ya avanzo despues de leerlo.
        token = Token(token_type, lexeme, self.line, self.column - len(lexeme))
        self.tokens.append(token)

    def tokenize(self) -> list[Token]:
        """Recorre todo el texto y devuelve la lista final de tokens.

        Aqui se decide si cada parte del texto es una palabra reservada, un
        identificador, un numero, un operador o un simbolo de puntuacion.
        """
        # Recorre todo el texto fuente y clasifica cada caracter o secuencia
        # relevante en tokens que el parser pueda consumir.
        while self.pos < len(self.text):
            self.skip_whitespace()

            if self.pos >= len(self.text):
                break

            char = self.peek()

            # Los saltos de linea no son significativos para esta gramatica.
            if char == "\n":
                self.advance()
                continue

            # Maneja archivos con finales de linea Windows (\r\n) o Mac viejos.
            if char == "\r":
                self.advance()
                if self.peek() == "\n":
                    self.advance()
                continue

            # Reconoce ":" usado despues del nombre de una regla.
            if char == ":":
                self.advance()
                self.add_token(TokenType.COLON, ":")
                continue

            # Reconoce el operador relacional mayor que.
            if char == ">":
                self.advance()
                self.add_token(TokenType.GT, ">")
                continue

            # Reconoce el operador relacional menor que.
            if char == "<":
                self.advance()
                self.add_token(TokenType.LT, "<")
                continue

            # Reconoce el operador relacional de igualdad.
            if char == "=":
                self.advance()
                self.add_token(TokenType.EQ, "=")
                continue

            # Reconoce valores numericos enteros.
            if char.isdigit():
                value = self.read_number()
                self.add_token(TokenType.VALUE, value)
                continue

            # Reconoce identificadores y los convierte en keywords cuando
            # coinciden exactamente con la tabla KEYWORDS.
            if char.isalpha() or char == "_":
                identifier = self.read_identifier()
                token_type = self.KEYWORDS.get(identifier, TokenType.ID)
                self.add_token(token_type, identifier)
                continue

            # Cualquier otro caracter no pertenece al lenguaje soportado.
            self.error(f"Unexpected character: {char!r}")

        # EOF marca el final para que el parser pueda verificar que no sobro
        # entrada sin consumir.
        self.add_token(TokenType.EOF, "")
        return self.tokens


def tokenize(text: str) -> list[Token]:
    """Funcion corta para tokenizar texto sin crear el Lexer manualmente."""
    # Envoltorio simple para usar el lexer sin instanciarlo manualmente.
    lexer = Lexer(text)
    return lexer.tokenize()


if __name__ == "__main__":
    # Prueba manual rapida: tokeniza dos reglas y muestra cada token generado.
    code = """rule r1:
if temp > 30 then alert

rule r2:
if alert AND active then notify
"""

    tokens = tokenize(code)
    for token in tokens:
        print(token)

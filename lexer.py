"""Lexical analyzer (tokenizer) for the rule-based language."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """Enumeration of all token types in the rule language."""

    # Keywords
    RULE = auto()
    IF = auto()
    THEN = auto()
    AND = auto()

    # Operators
    COLON = auto()  # :
    GT = auto()  # >
    LT = auto()  # <
    EQ = auto()  # =

    # Literals
    ID = auto()  # Identifiers
    VALUE = auto()  # Integer values

    # Special
    EOF = auto()
    NEWLINE = auto()


@dataclass
class Token:
    """A single token with its type and lexeme."""

    type: TokenType
    lexeme: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.lexeme!r}, {self.line}, {self.column})"


class Lexer:
    """Tokenizes rule-based language source code."""

    KEYWORDS = {
        "rule": TokenType.RULE,
        "if": TokenType.IF,
        "then": TokenType.THEN,
        "AND": TokenType.AND,
    }

    def __init__(self, text: str) -> None:
        """Initialize the lexer with source text.

        Args:
            text: The source code to tokenize.
        """
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []

    def error(self, message: str) -> None:
        """Raise a lexical error with position information."""
        raise SyntaxError(
            f"Lexical error at line {self.line}, column {self.column}: {message}"
        )

    def peek(self, offset: int = 0) -> str:
        """Look at a character without consuming it."""
        pos = self.pos + offset
        if pos < len(self.text):
            return self.text[pos]
        return "\0"

    def advance(self) -> str:
        """Consume and return the current character."""
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
        """Skip spaces and tabs (not newlines)."""
        while self.peek() in (" ", "\t"):
            self.advance()

    def skip_newlines_and_whitespace(self) -> None:
        """Skip whitespace including newlines."""
        while self.peek() in (" ", "\t", "\n", "\r"):
            self.advance()

    def read_identifier(self) -> str:
        """Read an identifier or keyword starting at current position."""
        start_pos = self.pos
        start_col = self.column

        while self.peek() and (self.peek().isalnum() or self.peek() == "_"):
            self.advance()

        return self.text[start_pos : self.pos]

    def read_number(self) -> str:
        """Read a numeric value starting at current position."""
        start_pos = self.pos

        while self.peek() and self.peek().isdigit():
            self.advance()

        return self.text[start_pos : self.pos]

    def add_token(self, token_type: TokenType, lexeme: str) -> None:
        """Add a token to the token list."""
        token = Token(token_type, lexeme, self.line, self.column - len(lexeme))
        self.tokens.append(token)

    def tokenize(self) -> list[Token]:
        """Tokenize the entire input and return list of tokens."""
        while self.pos < len(self.text):
            self.skip_whitespace()

            if self.pos >= len(self.text):
                break

            char = self.peek()

            # Skip newlines (they're not significant tokens)
            if char == "\n":
                self.advance()
                continue

            # Skip carriage returns
            if char == "\r":
                self.advance()
                if self.peek() == "\n":
                    self.advance()
                continue

            # Colon
            if char == ":":
                self.advance()
                self.add_token(TokenType.COLON, ":")
                continue

            # Greater than
            if char == ">":
                self.advance()
                self.add_token(TokenType.GT, ">")
                continue

            # Less than
            if char == "<":
                self.advance()
                self.add_token(TokenType.LT, "<")
                continue

            # Equals
            if char == "=":
                self.advance()
                self.add_token(TokenType.EQ, "=")
                continue

            # Numbers (values)
            if char.isdigit():
                value = self.read_number()
                self.add_token(TokenType.VALUE, value)
                continue

            # Identifiers and keywords
            if char.isalpha() or char == "_":
                identifier = self.read_identifier()
                token_type = self.KEYWORDS.get(identifier, TokenType.ID)
                self.add_token(token_type, identifier)
                continue

            # Unknown character
            self.error(f"Unexpected character: {char!r}")

        self.add_token(TokenType.EOF, "")
        return self.tokens


def tokenize(text: str) -> list[Token]:
    """Convenience function to tokenize text."""
    lexer = Lexer(text)
    return lexer.tokenize()


if __name__ == "__main__":
    # Simple test
    code = """rule r1:
if temp > 30 then alert

rule r2:
if alert AND active then notify
"""

    tokens = tokenize(code)
    for token in tokens:
        print(token)

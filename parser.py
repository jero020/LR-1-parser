"""LR(1)-compatible parser for the rule-based language.

This parser implements the grammar:
    Program → RuleList
    RuleList → Rule RuleList | ε
    Rule → rule id : if Cond then Action
    Cond → Cond AND Cond | Atom
    Atom → id RelOp value | id
    RelOp → > | < | =
    Action → id

The implementation uses recursive descent, which is compatible with LR(1).
"""

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
from lexer import Token, TokenType, tokenize


class ParseError(Exception):
    """Raised when a parsing error occurs."""

    pass


class Parser:
    """Recursive descent parser for the rule-based language."""

    def __init__(self, tokens: list[Token]) -> None:
        """Initialize parser with a list of tokens.

        Args:
            tokens: List of tokens from the lexer.
        """
        self.tokens = tokens
        self.pos = 0

    def error(self, message: str) -> None:
        """Raise a parse error with context information."""
        token = self.current_token()
        raise ParseError(
            f"Parse error at line {token.line}, column {token.column}: {message}. "
            f"Got {token.type.name} ({token.lexeme!r})"
        )

    def current_token(self) -> Token:
        """Get the current token without consuming it."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # Return EOF token

    def peek(self, offset: int = 0) -> Token:
        """Look ahead at a token without consuming it."""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # Return EOF token

    def advance(self) -> Token:
        """Consume and return the current token."""
        token = self.current_token()
        if token.type != TokenType.EOF:
            self.pos += 1
        return token

    def expect(self, token_type: TokenType) -> Token:
        """Consume a token of the expected type or raise an error."""
        token = self.current_token()
        if token.type != token_type:
            self.error(f"Expected {token_type.name}, got {token.type.name}")
        return self.advance()

    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        return self.current_token().type in token_types

    def parse(self) -> Program:
        """Parse the entire program."""
        rules = self.parse_rule_list()
        self.expect(TokenType.EOF)
        return Program(rules=rules)

    def parse_rule_list(self) -> list[Rule]:
        """Parse RuleList → Rule RuleList | ε"""
        rules: list[Rule] = []

        while self.match(TokenType.RULE):
            rules.append(self.parse_rule())

        return rules

    def parse_rule(self) -> Rule:
        """Parse Rule → rule id : if Cond then Action"""
        self.expect(TokenType.RULE)

        # Parse rule name (id)
        name_token = self.expect(TokenType.ID)
        rule_name = name_token.lexeme

        # Parse colon
        self.expect(TokenType.COLON)

        # Parse 'if'
        self.expect(TokenType.IF)

        # Parse condition
        condition = self.parse_condition()

        # Parse 'then'
        self.expect(TokenType.THEN)

        # Parse action
        action = self.parse_action()

        return Rule(name=rule_name, condition=condition, action=action)

    def parse_condition(self) -> Condition:
        """Parse Cond → Cond AND Cond | Atom

        This implements left-recursion elimination using iteration to handle
        left-associative AND operators.
        """
        left = self.parse_atom()

        while self.match(TokenType.AND):
            self.advance()  # consume AND
            right = self.parse_atom()
            left = AndCondition(left, right)

        return left

    def parse_atom(self) -> Condition:
        """Parse Atom → id RelOp value | id"""
        # Must start with an identifier
        if not self.match(TokenType.ID):
            self.error("Expected identifier in condition")

        identifier_token = self.advance()
        identifier = identifier_token.lexeme

        # Check if this is a comparison or a fact condition
        if self.match(TokenType.GT, TokenType.LT, TokenType.EQ):
            # It's a comparison
            operator_token = self.advance()
            operator = operator_token.lexeme

            # Expect a value
            value_token = self.expect(TokenType.VALUE)
            value = int(value_token.lexeme)

            return ComparisonCondition(
                identifier=identifier, operator=operator, value=value
            )
        else:
            # It's a fact condition
            return FactCondition(identifier=identifier)

    def parse_action(self) -> Action:
        """Parse Action → id"""
        identifier_token = self.expect(TokenType.ID)
        return Action(fact=identifier_token.lexeme)


def parse_program(text: str) -> Program:
    """Convenience function to parse a program from text.

    Args:
        text: The source code of the program.

    Returns:
        The parsed Program AST.

    Raises:
        SyntaxError: If lexical analysis fails.
        ParseError: If parsing fails.
    """
    tokens = tokenize(text)
    parser = Parser(tokens)
    return parser.parse()


if __name__ == "__main__":
    # Test parsing
    code = """rule r1:
if temp > 30 then alert

rule r2:
if alert AND active then notify
"""

    program = parse_program(code)
    print(f"Parsed {len(program.rules)} rules")
    for rule in program.rules:
        print(f"  Rule: {rule.name}")


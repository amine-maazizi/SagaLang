from lexer.token import Token
from lexer.token_type import TokenType

class Error:
    """Base class for all custom errors."""
    had_error: bool = False

    @staticmethod
    def report(line: int, column: int, message: str):
        print(f"SAGA::[line {line}, column {column}] Error: {message}")
        Error.had_error = True

    @staticmethod
    def error(token: Token, message: str):
        if token.type == TokenType:
            Error.report(token.line, token.column, f" at end {message}")
        else:
            Error.report(token.line, token.column, f" at '{token.lexeme}' {message}")

class ParseError(RuntimeError):
    """Custom exception for parser-related errors."""

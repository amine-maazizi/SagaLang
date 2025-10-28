from lexer.token import Token
from lexer.token_type import TokenType

class Error:
    """Base class for all custom errors."""
    had_error: bool = False
    had_runtime_error: bool = False

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

    @staticmethod
    def runtime_error(error: RuntimeError):
        print(f"SAGA::[line {error.token.line}, column {error.token.column}] Error: {error.message}")
        Error.had_runtime_error = True

class ParseError(RuntimeError):
    """Custom exception for parser-related errors."""

class RuntimeError(RuntimeError):
    def __init__(self, token, message):
        super().__init__(message)
        self.token = token
        self.message = message


class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class ReturnException(Exception):
    def __init__(self, value: any, *args):
        super().__init__(*args)
        self.value = value
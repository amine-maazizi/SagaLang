
class Error:
    """Base class for all custom errors."""
    had_error: bool = False

    @staticmethod
    def report(line: int, column: int, message: str):
        print(f"SAGA::[line {line}, column {column}] Error: {message}")
        Error.had_error = True

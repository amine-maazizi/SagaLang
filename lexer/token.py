from .token_type import TokenType

class Token:
    def __init__(self, type_: TokenType, lexeme: str, literal: any, line: int, column: int):
        self.type = type_
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        self.column = column

    def __repr__(self):
        return f'Token({self.type}, {self.lexeme}, {self.literal}, {self.line}, {self.column})'
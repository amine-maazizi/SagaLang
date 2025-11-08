from lexer.token import Token
from errors.errors import RuntimeError


class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name: str, value: any):
        # Only define in current scope
        self.values[name] = value

    def ancestor(self, distance: int):
        env: Environment = self
        for i in range(distance):
            env = env.enclosing
        return env

    def get_at(self, distance: int, name: str):
        return self.ancestor(distance).values.get(name)    

    def get(self, token):
        if token.lexeme in self.values:
            return self.values[token.lexeme]
        
        if self.enclosing:
            return self.enclosing.get(token)

        raise RuntimeError(token, f"Undefined variable '{token.lexeme}'.")

    def assign_at(self, distance: int, name: Token, value: any):
        self.ancestor(distance).values[name.lexeme] = value

    def assign(self, token, value: any):
        if token.lexeme in self.values:
            self.values[token.lexeme] = value
            return

        if self.enclosing:
            self.enclosing.assign(token, value)
            return

        raise RuntimeError(token, f"Undefined variable '{token.lexeme}'.")
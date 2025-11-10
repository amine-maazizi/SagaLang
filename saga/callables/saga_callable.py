from abc import ABC, abstractmethod
from typing import override

from stmt.stmt import Function
from environment.environment import Environment
from errors.errors import ReturnException

class SAGACallable(ABC):

    @abstractmethod
    def call(self, interpreter, arguments: list[any]):
        ...

    @abstractmethod
    def arity(self) -> int:
        ...

class SAGAFunction(SAGACallable):

    def __init__(self, declaration: Function, closure: Environment):
        self.declaration = declaration
        self.closure = closure
    
    @override
    def call(self, interpreter, arguments):
        env: Environment = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            env.define(self.declaration.params[i].lexeme, arguments[i])
        
        try:
            interpreter.execute_block(self.declaration.body, env)
        except ReturnException as return_value:
            return return_value.value

        return None
    
    @override
    def arity(self):
        return len(self.declaration.params)

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
    
class SAGAInstance():

    def __init__(self, saga_class):
        self.saga_class = saga_class
    
    def __repr__(self):
        return self.saga_class.name + " instance"

class SAGAClass(SAGACallable):

    def __init__(self, name: str):
        self.name = name
    
    def __repr__(self):
        return self.name
    
    @override
    def call(self, interpreter, arguments):
        instance: SAGAInstance = SAGAInstance(self)
        return instance

    @override
    def arity(self):
        return 0
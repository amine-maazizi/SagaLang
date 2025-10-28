from abc import ABC, abstractmethod
from typing import override

from lexer.token import Token

from expr.expr import Expr

class Stmt(ABC):
  @abstractmethod
  def accept(self, visitor: "Visitor"):
      pass

class Block(Stmt):
  def __init__(self, statements: list[Stmt]):
      self.statements = statements

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_block(self)

class Expression(Stmt):
  def __init__(self, expression: Expr):
      self.expression = expression

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_expression(self)

class Function(Stmt):
  def __init__(self, name: Token, params: list[Token], body: list[Stmt]):
      self.name = name
      self.params = params
      self.body = body

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_function(self)

class If(Stmt):
  def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Stmt):
      self.condition = condition
      self.then_branch = then_branch
      self.else_branch = else_branch

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_if(self)

class Say(Stmt):
  def __init__(self, expression: Expr):
      self.expression = expression

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_say(self)

class Return(Stmt):
  def __init__(self, keyword: Token, value: Expr):
      self.keyword = keyword
      self.value = value

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_return(self)

class Let(Stmt):
  def __init__(self, name: Token, initializer: Expr):
      self.name = name
      self.initializer = initializer

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_let(self)

class While(Stmt):
  def __init__(self, condition: Expr, body: Stmt):
      self.condition = condition
      self.body = body

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_while(self)

class Break(Stmt):
  def __init__(self):
      pass
  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_break(self)

class Continue(Stmt):
  def __init__(self):
      pass
  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_continue(self)

class Visitor(ABC):
  @abstractmethod
  def visit_block(self, stmt: Block):
      pass
  @abstractmethod
  def visit_expression(self, stmt: Expression):
      pass
  @abstractmethod
  def visit_function(self, stmt: Function):
      pass
  @abstractmethod
  def visit_if(self, stmt: If):
      pass
  @abstractmethod
  def visit_say(self, stmt: Say):
      pass
  @abstractmethod
  def visit_return(self, stmt: Return):
      pass
  @abstractmethod
  def visit_let(self, stmt: Let):
      pass
  @abstractmethod
  def visit_while(self, stmt: While):
      pass
  @abstractmethod
  def visit_break(self, stmt: Break):
      pass
  @abstractmethod
  def visit_continue(self, stmt: Continue):
      pass

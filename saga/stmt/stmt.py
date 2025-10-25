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

class Say(Stmt):
  def __init__(self, expression: Expr):
      self.expression = expression

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_say(self)

class Let(Stmt):
  def __init__(self, name: Token, initializer: Expr):
      self.name = name
      self.initializer = initializer

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_let(self)

class Visitor(ABC):
  @abstractmethod
  def visit_block(self, block: Block):
      pass
  @abstractmethod
  def visit_expression(self, expression: Expression):
      pass
  @abstractmethod
  def visit_say(self, say: Say):
      pass
  @abstractmethod
  def visit_let(self, let: Let):
      pass

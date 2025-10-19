from abc import ABC, abstractmethod
from typing import override

from lexer.token import Token

class Expr(ABC):
  @abstractmethod
  def accept(self, visitor: "Visitor"):
      pass

class Binary(Expr):
  def __init__(self, left: Expr, operator: Token, right: Expr):
      self.left = left
      self.operator = operator
      self.right = right

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_binary(self)

class Grouping(Expr):
  def __init__(self, expression: Expr):
      self.expression = expression

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_grouping(self)

class Literal(Expr):
  def __init__(self, value: any):
      self.value = value

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_literal(self)

class Unary(Expr):
  def __init__(self, operator: Token, right: Expr):
      self.operator = operator
      self.right = right

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_unary(self)

class Visitor(ABC):
  @abstractmethod
  def visit_binary(self, binary: Binary):
      pass
  @abstractmethod
  def visit_grouping(self, grouping: Grouping):
      pass
  @abstractmethod
  def visit_literal(self, literal: Literal):
      pass
  @abstractmethod
  def visit_unary(self, unary: Unary):
      pass

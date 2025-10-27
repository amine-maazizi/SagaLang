from abc import ABC, abstractmethod
from typing import override

from lexer.token import Token

class Expr(ABC):
  @abstractmethod
  def accept(self, visitor: "Visitor"):
      pass

class Assign(Expr):
  def __init__(self, name: Token, value: Expr):
      self.name = name
      self.value = value

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_assign(self)

class Binary(Expr):
  def __init__(self, left: Expr, operator: Token, right: Expr):
      self.left = left
      self.operator = operator
      self.right = right

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_binary(self)

class Call(Expr):
  def __init__(self, callee: Expr, paren: Token, arguments: list[Expr]):
      self.callee = callee
      self.paren = paren
      self.arguments = arguments

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_call(self)

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

class Logical(Expr):
  def __init__(self, left: Expr, operator: Token, right: Expr):
      self.left = left
      self.operator = operator
      self.right = right

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_logical(self)

class Ternary(Expr):
  def __init__(self, condition: Expr, then_branch: Expr, else_branch: Expr):
      self.condition = condition
      self.then_branch = then_branch
      self.else_branch = else_branch

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_ternary(self)

class Unary(Expr):
  def __init__(self, operator: Token, right: Expr):
      self.operator = operator
      self.right = right

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_unary(self)

class Variable(Expr):
  def __init__(self, name: Token):
      self.name = name

  @override
  def accept(self, visitor: "Visitor"):
      return visitor.visit_variable(self)

class Visitor(ABC):
  @abstractmethod
  def visit_assign(self, expr: Assign):
      pass
  @abstractmethod
  def visit_binary(self, expr: Binary):
      pass
  @abstractmethod
  def visit_call(self, expr: Call):
      pass
  @abstractmethod
  def visit_grouping(self, expr: Grouping):
      pass
  @abstractmethod
  def visit_literal(self, expr: Literal):
      pass
  @abstractmethod
  def visit_logical(self, expr: Logical):
      pass
  @abstractmethod
  def visit_ternary(self, expr: Ternary):
      pass
  @abstractmethod
  def visit_unary(self, expr: Unary):
      pass
  @abstractmethod
  def visit_variable(self, expr: Variable):
      pass

from lexer.token import Token
from lexer.token_type import TokenType
from expr.expr import Expr, Binary, Unary, Literal, Grouping

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0
    
    def expression(self):
        return self.equality()
    
    def equality(self):
        expr: Expr = self.comparaison()

        while (self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL)):
            operator: Token = self.previous()
            right: Expr = self.comparaison()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def comparaison(self):
        expr: Expr = self.term()

        while (self.match(
            TokenType.GREATER, TokenType.GREATER_EQUAL,
            TokenType.LESS, TokenType.LESS_EQUAL
        )):
            operator: Token = self.previous()
            right: Expr = self.term()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def term(self):
        expr: Expr = self.factor()

        while (self.match(
            TokenType.PLUS, TokenType.MINUS
        )):
            operator: Token = self.previous()
            right: Expr = self.factor()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def factor(self):
        expr: Expr = self.unary()

        while (self.match(
            TokenType.STAR, TokenType.SLASH
        )):
            operator: Token = self.previous()
            right: Expr = self.unary()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def unary(self):
        if (self.match(
            TokenType.BANG, TokenType.MINUS
        )):
            operator: Token = self.previous()
            return  Unary(operator, self.primary())
        
        return self.primary() 
    
    def primary(self):
        if self.match(TokenType.FALSE): return Literal(False)
        if self.match(TokenType.TRUE):  return Literal(True)
        if self.match(TokenType.NIL):   return Literal(None)

        if self.match(TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING):
            return Literal(self.previous().literal)
        
        if self.match(TokenType.LEFT_PAREN):
            expr: Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression.")
            return Grouping(expr)
    
    def match(self, *tokens):
        """
            Checks if the current token matches a set of candidate tokens 
            NOTE: I didn't convert the arguments into a set for an efficient lookup
            because the operation itself is O(n) => same complexity either way
        """
        matches = self.tokens[self.current].type in tokens
        self.current += 1
        return matches

    def previous(self):
        """Returns the previous token"""
        if self.current > 1:
            return self.tokens[self.current - 1]
    
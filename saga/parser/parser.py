from lexer.token import Token
from lexer.token_type import TokenType
from expr.expr import Expr, Binary, Unary, Literal, Grouping, Ternary 
from errors.errors import Error, ParseError

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self) -> Expr:
        try:
            return self.expression()
        except ParseError as error:
            self.synchronize()
            return None

    def expression(self):
        return self.comma()
    
    def comma(self):
        if self.match(TokenType.COMMA):
            operator: Token = self.previous()
            self.error(operator, "Binary operator ',' cannot appear at the beginning of an expression.")
            self.ternary() 
            raise ParseError()

        expr: Expr = self.ternary()

        while self.match(TokenType.COMMA):
            operator: Token = self.previous()
            right: Expr = self.ternary()
            expr = Binary(expr, operator, right)
        
        return expr

    def ternary(self):
        expr: Expr = self.equality()

        if self.match(TokenType.QUESTION):
            # recursivly parse the 'then' branch 
            then_branch: Expr = self.ternary()
            
            # Consume the colon
            self.consume(TokenType.COLON, "Expected ':' after then branch of ternary expression.")
            
            # recursivly parse the 'else' branch 
            else_branch: Expr = self.ternary()
            
            expr = Ternary(expr, then_branch, else_branch)
        
        return expr

    def equality(self):
        if self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self.previous()
            self.error(operator, f"Binary operator '{operator.lexeme}' cannot appear at the beginning of an expression.")
            self.comparison()  
            raise ParseError()

        expr: Expr = self.comparison()

        while (self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL)):
            operator: Token = self.previous()
            right: Expr = self.comparison()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def comparison(self):
        if self.match(TokenType.GREATER, TokenType.GREATER_EQUAL,
             TokenType.LESS, TokenType.LESS_EQUAL):
            operator: Token = self.previous()
            self.error(operator, f"Binary operator '{operator.lexeme}' cannot appear at the beginning of an expression.")
            self.term()  
            raise ParseError()

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
        if self.match(TokenType.PLUS):
            operator: Token = self.previous()
            self.error(operator, f"Binary operator '{operator.lexeme}' cannot appear at the beginning of an expression.")
            self.factor()  
            raise ParseError()

        expr: Expr = self.factor()

        while (self.match(
            TokenType.PLUS, TokenType.MINUS
        )):
            operator: Token = self.previous()
            right: Expr = self.factor()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def factor(self):
        if self.match(TokenType.STAR, TokenType.SLASH):
            operator: Token = self.previous()
            self.error(operator, f"Binary operator '{operator.lexeme}' cannot appear at the beginning of an expression.")
            self.unary()  # Parse and discard right operand
            raise ParseError()

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
    
        raise self.error(self.peek(), "Expected expression.")
    
    def match(self, *tokens) -> bool:
        """
            Checks if the current token matches a set of candidate tokens 
            NOTE: I didn't convert the arguments into a set for an efficient lookup
            because the operation itself is O(n) => same complexity either way
        """
        matches = self.peek().type in tokens
        if matches:
            self.advance()
        return matches

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def check(self, type: TokenType) -> bool:
        if self.is_at_end(): return False
        return self.peek().type == type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def previous(self) -> Token:
        if self.current > 0:
            return self.tokens[self.current - 1]
    
    def consume(self, type: TokenType, message: str):
        """Looks for the a token of the suggested type else it yields an error"""
        if self.check(type): return self.advance()
        raise self.error(self.peek(), message)
    
    def error(self, token: Token, message: str) -> ParseError:
        Error.error(token, message)
        return ParseError()
    
    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            # if we reach a dedent, it is likely the end of a block
            if self.previous().type == TokenType.DEDENT:
                return

            # check if the next token starts a new statement
            if self.peek().type in {
            TokenType.LET,
            TokenType.FN,
            TokenType.IF,
            TokenType.FOR,
            TokenType.WHILE,
            TokenType.CLASS,
            TokenType.RETURN,
            TokenType.IMPORT,
            TokenType.SAY,
            }:
                return        

            # stop on INDENT or NEWLINE 
            if self.peek().type == TokenType.INDENT:
                return
        
            self.advance()
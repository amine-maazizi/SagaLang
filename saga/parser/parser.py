from lexer.token import Token
from lexer.token_type import TokenType
from expr.expr import Expr, Assign, Binary, Unary, Literal, Grouping, Logical, Ternary, Variable
from stmt.stmt import Stmt, Block, Expression, Say, Let, If, While, Continue, Break
from errors.errors import Error, ParseError

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self) -> Expr:
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        
        return statements
    
    def declaration(self):
        try:
            if self.match(TokenType.LET): return self.var_declaration()
            return self.statement()
        except ParseError as error:
            self.synchronize()
            return None

    def var_declaration(self):
        name: Token = self.consume("Expected variable name.", TokenType.IDENTIFIER)

        initializer: Expr = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        
        self.consume("Expected newline or EOF after value.", TokenType.NEWLINE, TokenType.EOF)
        return Let(name, initializer)

    def statement(self) -> Stmt:
        if self.match(TokenType.FOR): return self.for_statement()
        if self.match(TokenType.IF): return self.if_statement()
        if self.match(TokenType.SAY): return self.say_statement()
        if self.match(TokenType.WHILE): return self.while_statement()
        if self.match(TokenType.BREAK): return self.break_statement()
        if self.match(TokenType.CONTINUE): return self.continue_statement()
        if self.match(TokenType.INDENT): return Block(self.block())

        return self.expression_statement()
    
    def break_statement(self):
        self.consume("Expected newline or EOF after 'break'.", TokenType.NEWLINE, TokenType.EOF)
        return Break()

    def continue_statement(self):
        self.consume("Expected newline or EOF after 'continue'.", TokenType.NEWLINE, TokenType.EOF)
        return Continue()

    def for_statement(self):
        # for i in 1..10:
        loop_var: Token = self.consume("Expected variable name after 'for'.", TokenType.IDENTIFIER)
        self.consume("Expected 'in' after loop variable.", TokenType.IN)
        iterable: Expr = self.expression()  # Parse range like 1..10
        self.consume("Expected ':' after iterable.", TokenType.COLON)
        self.consume("Expected newline after ':'.", TokenType.NEWLINE)
        
        body: Stmt = self.statement()
        
        # Desugar: for i in start..end  =>
        # {
        #   let i = start
        #   while i <= end:
        #       body
        #       i = i + 1
        # }
        
        # Assuming iterable is a Binary expression with RANGE operator
        if isinstance(iterable, Binary) and iterable.operator.type == TokenType.RANGE:
            start = iterable.left
            end = iterable.right
            
            # Create: let i = start
            initializer = Let(loop_var, start)
            
            # Create: i <= end
            condition = Binary(
                Variable(loop_var),
                Token(TokenType.LESS_EQUAL, "<=", None, loop_var.line, loop_var.column),
                end
            )
            
            # Create: i = i + 1
            increment = Expression(
                Assign(
                    loop_var,
                    Binary(
                        Variable(loop_var),
                        Token(TokenType.PLUS, "+", None, loop_var.line, loop_var.column),
                        Literal(1)
                    )
                )
            )
            
            # Create the while body: original body + increment
            while_body = Block([body, increment]) if isinstance(body, Block) else Block([body, increment])
            
            # Create the while loop
            while_stmt = While(condition, while_body)
            
            # Wrap everything in a block
            return Block([initializer, while_stmt])
        
        else:
            # Handle other iterables later
            Error.error(loop_var, "For loop currently only supports range expressions.")
            raise ParseError()

    def while_statement(self):
        condition: Expr = self.expression()
        self.consume("Expected ':' after condition.", TokenType.COLON)
        self.consume("Expected newline after ':'.", TokenType.NEWLINE)
        body: Stmt = self.statement()

        return While(condition, body)

    def if_statement(self):
        condition: Expr = self.expression()
        self.consume("Expected ':' after condition.", TokenType.COLON)
        self.consume("Expected newline after ':'.", TokenType.NEWLINE)

        then_branch: Stmt = self.statement()
        
        else_branch: Stmt = None


        if self.match(TokenType.ELSE):
            self.consume("Expected ':' after 'else' statement.", TokenType.COLON)
            self.consume("Expected newline after ':'.", TokenType.NEWLINE)
            else_branch: Stmt = self.statement()

        return If(condition, then_branch, else_branch)

    def say_statement(self):
        value: Expr = self.expression()
        self.consume("Expected newline or EOF after value.", TokenType.NEWLINE, TokenType.EOF)
        return Say(value)

    def expression_statement(self):
        expr: Expr = self.expression()
        self.consume("Expected newline or EOF after value.", TokenType.NEWLINE, TokenType.EOF)
        return Expression(expr)

    def block(self):
        statements: list[Stmt] = []

        while not self.is_at_end():
            if self.check(TokenType.DEDENT):
                break
            statements.append(self.declaration())

        # Only consume DEDENT if we haven't reached EOF
        if not self.is_at_end():
            self.consume("Expected dedentation after block.", TokenType.DEDENT)
        
        return statements

    def assignment(self):
        expr: Expr = self.logical_or()

        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: Expr = self.assignment()

            if isinstance(expr, Variable):
                name: Token = expr.name
                return Assign(name, value)

            Error.error(equals, "Invalid assignment target.")

        return expr

    def logical_or(self):
        expr: Expr = self.logical_and()

        while self.match(TokenType.OR):
            operator: Token = self.previous()
            right: Expr = self.logical_and()
            expr = Logical(expr, operator, right)

        return expr

    def logical_and(self):
        expr: Expr = self.equality()

        while self.match(TokenType.AND):
            operator: Token = self.previous()
            right: Expr = self.equality()
            expr = Logical(expr, operator, right)

        return expr

    def expression(self):
        return self.assignment()
    
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
            self.consume("Expected ':' after then branch of ternary expression.", TokenType.COLON)
            
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
            self.range_expr() 
            raise ParseError()

        expr: Expr = self.range_expr()

        while (self.match(
            TokenType.GREATER, TokenType.GREATER_EQUAL,
            TokenType.LESS, TokenType.LESS_EQUAL
        )):
            operator: Token = self.previous()
            right: Expr = self.range_expr()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def range_expr(self):
        expr: Expr = self.term()

        while self.match(TokenType.RANGE):
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
        
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expr: Expr = self.expression()
            self.consume("Expected ')' after expression.", TokenType.RIGHT_PAREN)
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
    
    def consume(self,  message: str, *types: TokenType):
        """Looks for the a token of the suggested type else it yields an error"""
        if self.peek().type in types: return self.advance()
        raise self.error(self.peek(), message)
    
    def error(self, token: Token, message: str) -> ParseError:
        Error.error(token, message)
        return ParseError()
    
    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().type == TokenType.NEWLINE:
                return

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
            TokenType.BREAK,
            TokenType.CONTINUE,
            }:
                return        

            self.advance()
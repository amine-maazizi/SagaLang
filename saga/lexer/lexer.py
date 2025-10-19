from .token_type import TokenType
from .token import Token
from errors.errors import Error

class Lexer:

    def __init__(self, source: str):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.indentation_level = 0
        self.at_line_start = False

        self.keywords = {
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "while": TokenType.WHILE,
            "for": TokenType.FOR,
            "return": TokenType.RETURN,
            "fn": TokenType.FN,
            "let": TokenType.LET,
            "true": TokenType.TRUE,
            "false": TokenType.FALSE,
            "nil": TokenType.NIL,
            "import": TokenType.IMPORT,
            "in": TokenType.IN,
            "say": TokenType.SAY,
            "class": TokenType.CLASS,
            "this": TokenType.THIS,
            "super": TokenType.SUPER
        }

    def lex_tokens(self) -> list[Token]:
        """Performs lexical analysis on the source string"""
        while not self.is_at_end():
            # start of the next lexeme
            self.start = self.current
            self.lex_token()
        
        # Append an EOF at then end of the token list
        self.tokens.append(Token(
            type_=TokenType.EOF,
            lexeme="",
            literal=None,
            line=self.line,
            column=self.column
        ))
    
    def is_at_end(self) -> bool:
        """Checks if the lexer has reached the end of the source file"""
        return self.current >= len(self.source)

    def lex_token(self):
        c = self.advance()

        if self.at_line_start and c == ' ':
            self.current -= 1  # Put back the space
            self.column -= 1
            self.handle_indentation()
            self.at_line_start = False
            return
        
        if c not in (' ', '\t', '\r'):
            self.at_line_start = False

        match c:
            case '(':
                self.add_token(TokenType.LEFT_PAREN)
            case ')':
                self.add_token(TokenType.RIGHT_PAREN)
            case '{':
                self.add_token(TokenType.LEFT_BRACE)
            case '}':
                self.add_token(TokenType.RIGHT_BRACE)
            case ',':
                self.add_token(TokenType.COMMA)
            case '.':
                if self.match('.'):
                    self.add_token(TokenType.RANGE)
                else:
                    self.add_token(TokenType.DOT)
            case '-':
                self.add_token(TokenType.MINUS)
            case '+':
                self.add_token(TokenType.PLUS)
            case '/':
                if self.match('/'):
                    while self.peek() != '\n' and not self.is_at_end():
                        self.advance()
                elif self.match('*'):
                    self.block_comment()
                else:
                    self.add_token(TokenType.SLASH)
            case '*':
                self.add_token(TokenType.STAR)
            case  ':':
                self.add_token(TokenType.COLON)
            case '<':
                if self.match('='):
                    self.add_token(TokenType.LESS_EQUAL)
                else:
                    self.add_token(TokenType.LESS)
            case '>':
                if self.match('='):
                    self.add_token(TokenType.GREATER_EQUAL)
                else:
                    self.add_token(TokenType.GREATER)
            case '=':
                if self.match('='):
                    self.add_token(TokenType.EQUAL_EQUAL)
                else:
                    self.add_token(TokenType.EQUAL)
            case '!':
                if self.match('='):
                    self.add_token(TokenType.BANG_EQUAL)
                else:
                    self.add_token(TokenType.BANG)
            case '\t' | '\r' | ' ':
                pass  # Ignore whitespace
            case '\n':
                self.line += 1
                self.column = 0
                self.at_line_start = True
            case '"':
                self.string()
            case _:
                if c.isdigit():
                    self.number()
                elif c.isalpha():
                    self.identifier()
                else:
                    Error.report(self.line, self.column, "Unexpected character")
    
    def advance(self):
        """Advances the lexer and returns the next character"""
        self.current += 1
        self.column += 1
        return self.source[self.current-1]
    
    def add_token(self, type_: TokenType):
        """Adds a non-literal token"""
        self.add_token_with_literal(type_, None)
    
    def add_token_with_literal(self, type_, literal: any):
        """Adss a token"""
        lexeme = self.source[self.start:self.current]
        self.tokens.append(
            Token(
                type_,
                lexeme,
                literal,
                self.line,
                self.column
            )
        )        

    def match(self, expected: chr) -> bool:
        """checks if the current character matches the expected character"""
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        self.column += 1
        return True

    def peek(self):
        """Lookahead method, works like advance but doesn't consume the token"""
        if self.is_at_end():
            return ''
        return self.source[self.current]

    def peek_next(self):
        """A second character lookahead"""
        if self.is_at_end():
            return ''
        return self.source[self.current+1]

    def string(self):
        """Adds a string litteral"""
        while self.peek() != '"' and not self.is_at_end():
            if self.peek()  == '\n':
                self.line += 1
            self.advance()

        if self.is_at_end():
            Error.report(self.line, self.column, "Unterminated string")
        
        # closing "
        self.advance()

        # Trim the quotes
        value = self.source[self.start+1:self.current-1]
        self.add_token_with_literal(TokenType.STRING, value)

    def number(self):
        """Adds an number Litteral"""
        # Integer part
        while self.peek().isdigit():
            self.advance()
            
        # Fraction
        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()  # consume the "."

            while self.peek().isdigit():
                self.advance()

            value = float(self.source[self.start:self.current])
            self.add_token_with_literal(TokenType.FLOAT, value)
        else:
            value = int(self.source[self.start:self.current])
            self.add_token_with_literal(TokenType.INTEGER, value)
    
    def identifier(self):
        """Reads & Adds an identifier keyword"""
        while self.peek().isalnum():
            self.advance()
        
        text = self.source[self.start:self.current]
        token_type = self.keywords.get(text)
        if not token_type:
            # generic identifer
            token_type = TokenType.IDENTIFIER
        self.add_token(token_type)
    
    def block_comment(self):
        """Handles C-style block comments"""
        nesting_level = 1

        while nesting_level > 0 and not self.is_at_end():
            c = self.advance()
            
            if c == '/' and self.match('*'):
                nesting_level += 1
            elif c == '*' and self.match('/'):
                nesting_level -= 1
            elif c == '\n':
                self.line += 1
        
        if nesting_level > 0:
            Error.report(self.line, self.column, "Unterminated block comment")

    def handle_indentation(self):
        """indents/dedents based on the reached level"""
        local_indentation_level = 1
        while self.peek() == ' ' and not self.is_at_end():
            self.advance()
            local_indentation_level += 1

        local_indentation_level = local_indentation_level // 4
    
        if local_indentation_level > self.indentation_level:
            self.indentation_level = local_indentation_level
            self.add_token(TokenType.INDENT)
        elif local_indentation_level < self.indentation_level:
            self.indentation_level = local_indentation_level
            self.add_token(TokenType.DEDENT)
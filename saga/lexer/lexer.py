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
        self.line_has_content = False  # Track if current line has significant tokens

        self.keywords = {
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "and": TokenType.AND,
            "or": TokenType.OR,
            "while": TokenType.WHILE,
            "for": TokenType.FOR,
            "break": TokenType.BREAK,
            "CONTINUE": TokenType.CONTINUE,
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

        return self.tokens

    def is_at_end(self) -> bool:
        """Checks if the lexer has reached the end of the source file"""
        return self.current >= len(self.source)

    def lex_token(self):
        # Handle indentation at the start of every line
        if self.at_line_start:
            self.handle_indentation()
            self.at_line_start = False
            # After handling indentation, check if we're at end
            if self.is_at_end():
                return
            self.start = self.current

        c = self.advance()

        # Mark line as having content for any non-whitespace character
        if c not in (' ', '\t', '\r', '\n'):
            self.line_has_content = True

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
                    # Single-line comment - don't mark as content
                    self.line_has_content = False
                    while self.peek() != '\n' and not self.is_at_end():
                        self.advance()
                elif self.match('*'):
                    # Block comment - don't mark as content
                    self.line_has_content = False
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
            case '?':
                self.add_token(TokenType.QUESTION)
            case '\t' | '\r' | ' ':
                pass  # Ignore whitespace
            case '\n':
                # Only emit NEWLINE if the line had actual content
                if self.line_has_content:
                    self.add_token(TokenType.NEWLINE)
                self.line += 1
                self.column = 0
                self.at_line_start = True
                self.line_has_content = False  # Reset for next line
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
        if self.current + 1 >= len(self.source):
            return ''
        return self.source[self.current+1]

    def peek_previous(self):
        """Backwards lookahead"""
        if self.current > 1:
            return self.source[self.current-2]

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
        while self.peek().isalnum() or self.peek() == '_':
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
        local_indentation_level = 0
        while self.peek() == ' ' and not self.is_at_end():
            self.advance()
            local_indentation_level += 1

        # Skip if this is a blank line (only whitespace before newline/EOF)
        if self.peek() == '\n' or self.is_at_end():
            return

        local_indentation_level = local_indentation_level // 4

        if local_indentation_level > self.indentation_level:
            # Only indent by one level at a time
            self.indentation_level = local_indentation_level
            self.line_has_content = True
            self.add_token(TokenType.INDENT)
        elif local_indentation_level < self.indentation_level:
            # Emit multiple DEDENTs if we jump multiple levels
            while self.indentation_level > local_indentation_level:
                self.line_has_content = True
                self.add_token(TokenType.DEDENT)
                self.indentation_level -= 1
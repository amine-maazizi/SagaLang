from enum import Enum

class TokenType(Enum):
    ### Single-character tokens ###
    # grouping symbols
    LEFT_PAREN = '('
    RIGHT_PAREN = ')'
    COMMA = ','
    DOT = '.'
    COLON = ':'

    # arithmetic operators
    MINUS = '-'
    PLUS = '+'
    SLASH = '/'
    STAR = '*'

    # comparison operators
    LESS = '<'
    GREATER = '>'
    EQUAL = '='
    BANG = '!'

    # Scope management
    INDENT = "INDENT"
    DEDENT = "DEDENT"

    ### two-character tokens ###
    # arithmetic operators
    PLUS_EQUAL = '+='
    MINUS_EQUAL = '-='
    STAR_EQUAL = '*='
    SLASH_EQUAL = '/='
    PLUS_PLUS = '++'
    MINUS_MINUS = '--'
    RANGE = '..'

    # comparison operators
    LESS_EQUAL = '<='
    GREATER_EQUAL = '>='
    EQUAL_EQUAL = '=='
    BANG_EQUAL = '!='

    ### literals ###
    IDENTIFIER = 'IDENTIFIER'
    STRING = 'STRING'
    INTEGER = 'INTEGER'
    FLOAT = 'FLOAT'

    ### keywords ###
    # control flow
    IMPORT = 'import'
    LET = 'let'
    FN = 'fun'
    IF = 'if'
    ELSE = 'else'
    WHILE = 'while'
    FOR = 'for'
    RETURN = 'return'
    IN = 'in'

    # boolean literals
    TRUE = 'true'
    FALSE = 'false'
    NIL = 'nil'

    # Printing
    SAY = 'say'

    # object-oriented
    CLASS = 'class'
    THIS = 'this'
    SUPER = 'super'

    # end of file
    EOF = 'EOF'

    

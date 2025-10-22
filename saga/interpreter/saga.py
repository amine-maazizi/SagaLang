import sys

from lexer.lexer import Lexer
from parser.parser import Parser
from errors.errors import Error
from expr.expr import Expr
from ast_printer import AstPrinter

def run_file(path: str):
    try:
        f = open(path, 'r')
    except OSError:
        Error.had_error = True
        sys.exit()

    with f:
        run(f.read())
    
def run_prompt():
    """REPL (Read-Eval-Print Loop) for interactive usage"""
    line = input("SAGA> ")
    while line.strip() != 'q':
        run(line)
        Error.had_error = False
        line = input("SAGA> ")


def run(source: str):
    """Tokenizes, Parses & Interprets source code"""
    lex: Lexer = Lexer(source)
    lex.lex_tokens()
    parser: Parser = Parser(lex.tokens)
    expression: Expr = parser.parse()

    if Error.had_error: return

    print(AstPrinter(expression))


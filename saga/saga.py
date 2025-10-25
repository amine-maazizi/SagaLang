import sys

from lexer.lexer import Lexer
from parser.parser import Parser
from interpreter.interpreter import Interpreter
from errors.errors import Error
from lexer.token import Token
from stmt.stmt import Stmt


interpreter = Interpreter()

def run_file(path: str):
    try:
        f = open(path, 'r')
    except OSError:
        Error.had_error = True
        sys.exit()

    with f:
        run(f.read())

        if Error.had_error:
            sys.exit(65)
        if Error.had_runtime_error:
            sys.exit(70)
    
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
    tokens: list[Token] = lex.lex_tokens()
    parser: Parser = Parser(tokens)
    statements: list[Stmt] = parser.parse()

    if Error.had_error: return

    interpreter.interpret(statements)


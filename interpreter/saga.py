import sys

from lexer.lexer import Lexer
from errors.errors import Error

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
    lex = Lexer(source)
    lex.lex_tokens()

    # for now we will print each token of the input
    for token in lex.tokens:
        print(token)



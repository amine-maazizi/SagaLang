import sys

from lexer.lexer import Lexer
from parser.parser import Parser
from interpreter.interpreter import Interpreter
from errors.errors import Error
from lexer.token import Token
from stmt.stmt import Stmt, Expression
from resolver.resolver import Resolver


interpreter = Interpreter()

def run_file(path: str):
    try:
        f = open(path, 'r')
    except OSError:
        Error.had_error = True
        sys.exit()

    with f:
        run(f.read(), is_repl=False)

        if Error.had_error:
            sys.exit(65)
        if Error.had_runtime_error:
            sys.exit(70)
    
def run_prompt():
    """REPL (Read-Eval-Print Loop) for interactive usage"""
    line = input("SAGA> ")
    while line.strip() != 'q':
        run(line, is_repl=True)
        Error.had_error = False
        line = input("SAGA> ")


def run(source: str, is_repl: bool = False):
    """Tokenizes, Parses & Interprets source code"""
    lex: Lexer = Lexer(source)
    tokens: list[Token] = lex.lex_tokens()
    parser: Parser = Parser(tokens)
    statements: list[Stmt] = parser.parse()

    if Error.had_error: return

    resolver: Resolver = Resolver(interpreter)
    resolver.resolve(statements)

    if Error.had_error: return

    if is_repl and len(statements) == 1 and isinstance(statements[0], Expression):
        value = interpreter.evaluate(statements[0].expression)
        if value is not None:
            print(value)
    else:
        interpreter.interpret(statements)
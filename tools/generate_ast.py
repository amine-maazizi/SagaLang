import os
import sys

def define_ast(output_dir: str, base_name: str, types: list[str]):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, base_name.lower() + ".py")

    with open(path, 'w+') as f:
        f.write('from abc import ABC, abstractmethod\n')
        f.write('from typing import override\n\n')
        f.write('from lexer.token import Token\n\n')
        match base_name:
            case "Stmt":
                f.write("from expr.expr import Expr\n\n")
        f.write(f'class {base_name}(ABC):\n')
        f.write(f'  @abstractmethod\n')
        f.write(f'  def accept(self, visitor: "Visitor"):\n')
        f.write(f'      pass\n\n')

        for type in types:
            elements = type.split("|")
            if len(elements) == 2:
                class_name = elements[0].strip()
                fields =  elements[1].strip()
            else:
                class_name = elements[0]
                fields = None
            define_type(f, base_name, class_name, fields)

        define_visitor(f,base_name, types)

def define_type(f, base_name: str, class_name: str, field_list: list[str] = None):
    f.write(f'class {class_name}({base_name}):\n')
    
    # constructor
    if field_list:
        f.write(f'  def __init__(self, {field_list}):\n')
    else:
        f.write(f'  def __init__(self):\n')
    
    if field_list:
        fields = field_list.split(',')
        for field in fields:
            name = field.split(':')[0].lstrip()
            f.write(f'      self.{name} = {name}\n')
    else:
        f.write(f'      pass')

    f.write('\n')

    f.write(f'  @override\n')
    f.write(f'  def accept(self, visitor: "Visitor"):\n')
    f.write(f'      return visitor.visit_{class_name.lower()}(self)\n\n')

def define_visitor(f, base_name: str, types: list[str]):
    f.write(f'class Visitor(ABC):\n')
    for type in types:
        type_name = type.split('|')[0].strip()
        f.write(f'  @abstractmethod\n')
        f.write(f'  def visit_{type_name.lower()}(self, {base_name.lower()}: {type_name}):\n')
        f.write(f'      pass\n')

if __name__ == "__main__":
    args, argn = sys.argv, len(sys.argv)
    if argn != 2:
        sys.exit('Usage: generate_ast [output_dir]')
    
    output_dir = args[1]

    # define_ast(output_dir, "Expr", [
    #     "Assign     | name: Token, value: Expr",
    #     "Binary     | left: Expr, operator: Token, right: Expr",
    #     "Call       | callee: Expr, paren: Token, arguments: list[Expr]",
    #     "Grouping   | expression: Expr",
    #     "Literal    | value: any",
    #     "Logical    | left: Expr, operator: Token, right: Expr",
    #     "Ternary    | condition: Expr, then_branch: Expr, else_branch: Expr",
    #     "Unary      | operator: Token, right: Expr",
    #     "Variable   | name: Token"
    # ])

    define_ast(output_dir, "Stmt", [
        "Block      | statements: list[Stmt]",
        "Expression | expression: Expr",
        "Function   | name: Token, params: list[Token], body: list[Stmt]",
        "If         | condition: Expr, then_branch: Stmt, else_branch: Stmt",
        "Say        | expression: Expr",
        "Let        | name: Token, initializer: Expr",
        "While      | condition: Expr, body: Stmt",
        "Break",
        "Continue"
    ])
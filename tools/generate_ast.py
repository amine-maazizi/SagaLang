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
            class_name = type.split("|")[0].strip()
            fields =  type.split("|")[1].strip()
            define_type(f, base_name, class_name, fields)

        define_visitor(f, types)

def define_type(f, base_name: str, class_name: str, field_list: list[str]):
    f.write(f'class {class_name}({base_name}):\n')
    
    # constructor
    f.write(f'  def __init__(self, {field_list}):\n')
    
    fields = field_list.split(',')
    for field in fields:
        name = field.split(':')[0].lstrip()
        f.write(f'      self.{name} = {name}\n')
    
    f.write('\n')

    f.write(f'  @override\n')
    f.write(f'  def accept(self, visitor: "Visitor"):\n')
    f.write(f'      return visitor.visit_{class_name.lower()}(self)\n\n')

def define_visitor(f, types: list[str]):
    f.write(f'class Visitor(ABC):\n')
    for type in types:
        type_name = type.split('|')[0].strip()
        f.write(f'  @abstractmethod\n')
        f.write(f'  def visit_{type_name.lower()}(self, {type_name.lower()}: {type_name}):\n')
        f.write(f'      pass\n')

if __name__ == "__main__":
    args, argn = sys.argv, len(sys.argv)
    if argn != 2:
        sys.exit('Usage: generate_ast [output_dir]')
    
    output_dir = args[1]

    define_ast(output_dir, "Expr", [
        "Assign     | name: Token, value: Expr",
        "Binary     | left: Expr, operator: Token, right: Expr",
        "Grouping   | expression: Expr",
        "Literal    | value: any",
        "Ternary    | condition: Expr, then_branch: Expr, else_branch: Expr",
        "Unary      | operator: Token, right: Expr",
        "Variable   | name: Token"
    ])

    # define_ast(output_dir, "Stmt", [
    #     "Expression | expression: Expr",
    #     "Say        | expression: Expr",
    #     "Let        | name: Token, initializer: Expr"
    # ])
# SagaLang

A dynamically-typed interpreted language with Python-like syntax, built from scratch in Python.

## Overview

Saga is a clean, readable interpreted language featuring lexical scoping, first-class functions, closures, and object-oriented programming. Inspired by Lox from Crafting Interpreters, this project demonstrates fundamental compiler construction principles through a fully functional implementation with a custom lexer, parser, and tree-walk interpreter.

## Project Status

### Core Language: Complete

- ✅ Lexer with full tokenization
- ✅ Recursive descent parser generating abstract syntax trees
- ✅ Tree-walk interpreter with environment-based scoping
- ✅ Expression evaluation (arithmetic, logical, comparison)
- ✅ Statement execution (declarations, assignments, blocks)
- ✅ Control flow (if/else, while, for loops with break)
- ✅ First-class functions with closures
- ✅ Native functions (clock, random, file I/O, user input)
- ✅ Visual Studio Code extension with language support and syntax highlighting 

### In Development

- 🚧 Object-oriented programming (classes, inheritance, this)
- 🚧 Standard library for 2D rendering and real-time graphics
- 🚧 Neural code completion using pretrained transformer models
- 🚧 Extend the VS Code extension with:
  - Code snippets
  - Language server support
  - Debugging capabilities

## Quick Start

```bash# Run a Saga program
python saga/cmd/main.py examples/game.saga

# Interactive REPL
python saga/cmd/main.py
```

### Hello World
```python
say "Hello, Saga!"
```

### Closures in Action
```python
fun make_counter():
    let i = 0
    fun count():
        i = i + 1
        say i
    return count

let counter = make_counter()
counter()  # 1
counter()  # 2
```

## Language Reference
### Variables & Types
```python
let name = "Saga"        # String
let year = 2025          # Number
let active = true        # Boolean
let nothing = nil        # Nil

# Reassignment
name = "Updated"
```

**Supported Types**: `Number`, `String`, `Boolean`, `Nil`

### Operators

```python
# Arithmetic
1 + 2 - 3 * 4 / 5

# Comparison
x > 10
y <= 5

# Logical
(x > 0) and (y < 100)
is_ready or has_backup
!is_locked
```

### Control Flow
#### Conditionals
```python
if player_health < 30 and has_potion:
    player_health = 75
    has_potion = false
    say "Potion used! HP restored."
```

#### While Loops
```python
while player_health > 0:
    say "Fighting..."
    player_health = player_health - 20
```

#### For Loops
```python
for i in 1..5:
    say "Turn " + i
    if player_health <= 0:
        break
```

### Functions
```python
fun greet(name):
    say "Hello, " + name

greet("world")

# With return values
fun add(a, b):
    return a + b

let result = add(5, 3)
```

#### Functions are first-class values:
```python
let operation = add
say operation(10, 20)
```

### Classes & Inheritance
```python
class Animal:
    fun init(name):
        this.name = name
    
    fun speak():
        say this.name + " makes a sound"

class Dog < Animal:
    fun speak():
        say this.name + " barks!"

let buddy = Dog("Buddy")
buddy.speak()  # "Buddy barks!"
```
### Closures
```python
fun makeFibonacci():
    let a = 0
    let b = 1
    
    fun next():
        let temp = a
        a = b
        b = temp + b
        return temp
    
    return next

let fib = makeFibonacci()
for i in 0..10:
    say fib()
```

### Native Functions

| Function | Description | Example |
|----------|-------------|---------|
| `clock()` | Unix timestamp (seconds) | `let t = clock()` |
| `random()` | Random float [0, 1) | `let r = random()` |
| `random_int(min, max)` | Random integer [min, max] | `random_int(1, 10)` |
| `read_file(path)` | Read file contents | `let data = read_file("config.txt")` |
| `write_file(path, content)` | Write to file | `write_file("log.txt", "Hello")` |
| `append_file(path, content)` | Append to file | `append_file("log.txt", "World")` |
| `delete_file(path)` | Delete file | `delete_file("temp.txt")` |
| `file_exists(path)` | Check file existence | `if file_exists("data.txt"):` |
| `input(prompt)` | Get user input | `let name = input("Name: ")` |
## Example Programs

### Game Logic with Conditionals
```python
let player_health = 100
let has_potion = false
let in_safe_zone = false

if player_health > 0:
    if player_health < 30 and has_potion:
        player_health = 75
        has_potion = false
        say "You used a potion! Health restored. Current HP: " + player_health
    
    if player_health < 50 or in_safe_zone:
        say "You take a breather and plan your next move."
    
    if player_health >= 50 and !in_safe_zone:
        say "You feel strong and ready for battle!"
else:
    say "Player has been defeated!"
    say "Game Over"
```
### Battle Loop
```python
let player_health = 50
let has_potion = true

while player_health > 0:
    say "An enemy attacks!"
    player_health = player_health - 20

    if player_health <= 25 and has_potion:
        say "You use a potion to recover!"
        player_health = 75
        has_potion = false
    else:
        say "Current HP: " + player_health

    if player_health <= 0 or !has_potion and player_health <= 25:
        say "You are defeated!"

for i in 1..5:
    say "Turn " + i
    player_health = player_health - 5
    if player_health <= 0:
        say "You are defeated during turn " + i
        break
    else:
        say "Current HP after turn " + i + ": " + player_health
```
### Native Functions Demo
```python
say "--- Clock & Random ---"
let start = clock()
say "Current timestamp: " + start
say "Random float: " + random()
say "Random int (1-10): " + random_int(1, 10)

say "--- File Operations ---"
let filename = "test_output.txt"
write_file(filename, "Hello from SAGA!\n")
append_file(filename, "Second line!\n")

if file_exists(filename):
    let content = read_file(filename)
    say "File content:\n" + content
    delete_file(filename)
```

## Architecture

```text
saga/
├── lexer.py          # Tokenization and lexical analysis
├── parser.py         # Recursive descent parser, AST generation
├── interpreter.py    # Tree-walk interpreter with environment
├── ast_nodes.py      # AST node definitions
├── environment.py    # Variable scope management
├── natives.py        # Built-in functions
├── examples/         # Sample Saga programs
│   ├── game.saga
│   ├── closures.saga
│   └── natives.saga
├── stdlib/           # [WIP] Standard library modules
│   └── graphics.py   # 2D rendering primitives
└── ml/               # [WIP] Neural code completion
    └── completion.py # Transformer-based suggestions
## Upcoming Features

### Standard Library (Graphics)
```python
import graphics

let win = graphics.window(800, 600, "Saga Graphics")
let rect = graphics.rectangle(100, 100, 50, 50, "blue")
win.add(rect)
win.render()
```

#### Planned API:
- Window management and event loop
- Primitive shapes (rectangles, circles, lines)
- Sprite rendering and transformations
- Real-time updates at 60fps

### Neural Code Completion
```python
# Type "fun fib" and get AI-powered suggestions
fun fibonacci(n):
    # [AI suggests]: if n <= 1: return n
    # [AI suggests]: return fibonacci(n-1) + fibonacci(n-2)
```

#### Implementation:
- Fine-tuned GPT-2/CodeGen model on Saga syntax
- Context-aware completions using AST state
- VSCode extension integration

## Technical Highlights

- **Lexical Scoping**: Variables resolved at parse time using environment chains
- **Closures**: Functions capture surrounding scope for powerful abstractions
- **Tree-Walk Interpreter**: Direct AST evaluation (future: bytecode VM)
- **Visitor Pattern**: Clean separation between AST nodes and interpretation logic
- **Native Interop**: Easy Python function binding for extending functionality

## Learning Resources

This project extends beyond concepts from:

- [Crafting Interpreters](https://craftinginterpreters.com/) by Robert Nystrom

## Future Directions

- 🎯 Bytecode compiler and stack-based VM for performance
- 🎯 Garbage collector with mark-and-sweep
- 🎯 Module system and package manager
- 🎯 Debugger with breakpoints and stack inspection
- 🎯 VSCode extension with syntax highlighting

## License

MIT License - see [LICENSE](LICENSE) file for details


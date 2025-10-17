# The Saga Language

Saga is a small, human-readable interpreted language inspired by Lox from Crafting Interpreters. It's dynamically typed, lexically scoped, and built for clarity over complexity. This section describes every feature the language supports.

## Basics

```
say "Hello, world"
```

- Comments begin with `//`
- Statements end with a newline (or `;`)
- Strings use double quotes `"text"`
- `nil` represents the absence of a value

## Variables
```
let name = "Ada"
let year = 2025

say name + " was here in " + year
```

- Variables are declared with `let`
- They can be reassigned:
```
name = "Alan"
```

## Data Types

| Type | Example |
|------|---------|
| Number | `123`, `3.14` |
| String | `"hello"` |
| Boolean | `true`, `false` |
| Nil | `nil` |
| List (optional if you add it) | `[1, 2, 3]` |

Arithmetic and comparison:
```
1 + 2 * 3 / 4 - 5
(3 > 2) and (2 < 5)
```

## Control Flow

### If / Else
```
if condition:
    say "yes"
else:
    say "no"
```

### While Loop
```
while i < 10:
    say i
    i = i + 1
```

### For Loop (syntactic sugar)
```
for i in 0..10:
    say i
```

## Functions
```
fun greet(name):
    say "Hello, " + name

greet("Saga")
```

Functions can return values:
```
fun add(a, b):
    return a + b
```

Functions are first-class:
```
let f = add
say f(2, 3)
```

## Scope and Closures

Saga uses lexical scoping — inner blocks capture outer variables.
```
fun counter():
    let i = 0
    fun next():
        i = i + 1
        return i
    return next

let count = counter()
say count()  // 1
say count()  // 2
```

## Classes
```
class Animal:
    fun speak():
        say "noise"
```

Instances:
```
let dog = Animal()
dog.speak()
```

Constructors (`init`):
```
class Dog:
    fun init(name):
        this.name = name
    fun speak():
        say this.name + " says woof"
```

Inheritance:
```
class Beagle < Dog:
    fun speak():
        say this.name + " says arooo!"
```

## Built-ins

| Function | Description |
|----------|-------------|
| `say(value)` | Prints to console |
| `clock()` | Returns time in seconds |
| `type(value)` | Returns `"number"`, `"string"`, etc. |

(You can expand this later with native Python bindings.)

## Error Handling (optional extension)

If you want exceptions like in clox, you can add this later:
```
try:
    risky()
catch err:
    say "Error: " + err
```

## Example Program
```
class Person:
    fun init(name):
        this.name = name
    fun greet():
        say "Hello, I'm " + this.name

fun main():
    let ada = Person("Ada")
    ada.greet()

main()
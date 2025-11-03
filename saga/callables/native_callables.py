from typing import override
from time import time
import random
import sys

from callables.saga_callable import SAGACallable

class ClockCallable(SAGACallable):
    @override
    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        return time()
    
    def __str__(self):
        return "<native fn>"


class RandomCallable(SAGACallable):
    """Returns a random float between 0.0 and 1.0"""
    @override
    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        return random.random()
    
    def __str__(self):
        return "<native fn>"


class RandomIntCallable(SAGACallable):
    """Returns a random integer between min and max (inclusive)"""
    @override
    def arity(self):
        return 2
    
    def call(self, interpreter, arguments):
        min_val = int(arguments[0])
        max_val = int(arguments[1])
        return random.randint(min_val, max_val)
    
    def __str__(self):
        return "<native fn>"


class InputCallable(SAGACallable):
    """Reads a line from user input, optional prompt"""
    @override
    def arity(self):
        return -1  # variadic: 0 or 1 argument
    
    def call(self, interpreter, arguments):
        if len(arguments) == 0:
            return input()
        elif len(arguments) == 1:
            return input(str(arguments[0]))
        else:
            raise RuntimeError("input() takes 0 or 1 arguments")
    
    def __str__(self):
        return "<native fn>"


class ReadFileCallable(SAGACallable):
    """Reads entire file and returns as string"""
    @override
    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        filename = str(arguments[0])
        try:
            with open(filename, 'r') as f:
                return f.read()
        except FileNotFoundError:
            raise RuntimeError(f"File not found: {filename}")
        except IOError as e:
            raise RuntimeError(f"Error reading file: {str(e)}")
    
    def __str__(self):
        return "<native fn>"


class WriteFileCallable(SAGACallable):
    """Writes content to file (overwrites)"""
    @override
    def arity(self):
        return 2
    
    def call(self, interpreter, arguments):
        filename = str(arguments[0])
        content = str(arguments[1])
        try:
            with open(filename, 'w') as f:
                f.write(content)
            return None
        except IOError as e:
            raise RuntimeError(f"Error writing file: {str(e)}")
    
    def __str__(self):
        return "<native fn>"


class AppendFileCallable(SAGACallable):
    """Appends content to file"""
    @override
    def arity(self):
        return 2
    
    def call(self, interpreter, arguments):
        filename = str(arguments[0])
        content = str(arguments[1])
        try:
            with open(filename, 'a') as f:
                f.write(content)
            return None
        except IOError as e:
            raise RuntimeError(f"Error appending to file: {str(e)}")
    
    def __str__(self):
        return "<native fn>"


class FileExistsCallable(SAGACallable):
    """Checks if file exists"""
    @override
    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        import os
        filename = str(arguments[0])
        return os.path.isfile(filename)
    
    def __str__(self):
        return "<native fn>"


class DeleteFileCallable(SAGACallable):
    """Deletes a file"""
    @override
    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        import os
        filename = str(arguments[0])
        try:
            os.remove(filename)
            return None
        except FileNotFoundError:
            raise RuntimeError(f"File not found: {filename}")
        except IOError as e:
            raise RuntimeError(f"Error deleting file: {str(e)}")
    
    def __str__(self):
        return "<native fn>"


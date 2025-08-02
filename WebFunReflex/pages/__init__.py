import os
import importlib

# Get all .py files in current directory except __init__.py
py_files = [
    f[:-3] for f in os.listdir(os.path.dirname(__file__)) 
    if f.endswith('.py') and f != '__init__.py'
]

# Import all modules dynamically
_globals = globals()
for module in py_files:
    _globals[module] = importlib.import_module(f'.{module}', package=__name__)

__all__ = py_files

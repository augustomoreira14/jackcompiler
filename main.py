from CompilationEngine import CompilationEngine
from xml.sax.saxutils import escape
import sys
from os import path, listdir

try:
    if path.isdir(sys.argv[1]):
        files = listdir(sys.argv[1])
        for file in files:
            if file.endswith('.jack'):
                compilation = CompilationEngine(file)
                compilation.compile()

    elif path.isfile(sys.argv[1]):
        compilation = CompilationEngine(sys.argv[1])
        compilation.compile()
    else:
        raise FileNotFoundError
        
    
except FileNotFoundError:
    print("File not found.")


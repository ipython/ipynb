
# coding: utf-8

# # Compilation
# 
# Compilation occurs in the __3__ steps:
# 
# 1. Text is transformed into a valid source string.
# 2. The source string is parsed into an abstract syntax tree
# 3. The abstract syntax compiles to valid bytecode 

# In[1]:


from nbconvert.exporters.notebook import NotebookExporter


# In[2]:


from IPython.core.compilerop import CachingCompiler
from dataclasses import dataclass, field
from nbformat import NotebookNode
import ast

class Compiler(CachingCompiler):
    """{Shell} provides the IPython machinery to objects."""
    filename: str = '<Shell>'            
    @property
    def ip(Compiler): 
        """The current interactive shell"""
        from IPython import get_ipython
        from IPython.core.interactiveshell import InteractiveShell
        return get_ipython() or InteractiveShell()
    
    def ast_transform(Compiler, node):
        for visitor in Compiler.ip.ast_transformers: 
            node = visitor.visit(node)
        return node
    
    @property
    def transform(Compiler): return Compiler.ip.input_transformer_manager.transform_cell

    def compile(Compiler, ast): 
        """Compile AST to bytecode using the an IPython compiler."""
        return (Compiler.ip and Compiler.ip.compile or CachingCompiler())(ast, Compiler.filename, 'exec')
            
    def ast_parse(Compiler, source, filename='<unknown>', symbol='exec', lineno=0): 
        return ast.increment_lineno(super().ast_parse(source, Compiler.filename, 'exec'), lineno)



# In[3]:


if __name__ ==  '__main__':
    from pathlib import Path
    from nbconvert.exporters.script import ScriptExporter
    Path('compiler_ipython.py').write_text(ScriptExporter().from_filename('compiler_ipython.ipynb')[0])
    __import__('doctest').testmod()


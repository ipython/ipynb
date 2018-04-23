
# coding: utf-8

# # Decoding
# 
# If a notebook is imported, it should provide a natural __traceback__ experience similar to python imports.  The `importnb` importer creates a just decoder object that retains line numbers to the raw json when the notebook is imported.

# In[1]:


from json.decoder import JSONObject, JSONDecoder, WHITESPACE, WHITESPACE_STR    
from nbformat import NotebookNode
class LineNoDecoder(JSONDecoder):
    """A JSON Decoder to return a NotebookNode with lines numbers in the metadata."""
    def __init__(self, *, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, strict=True, object_pairs_hook=None):
        from json.scanner import py_make_scanner    
        super().__init__(object_hook=object_hook, parse_float=parse_float, parse_int=parse_int, parse_constant=parse_constant, strict=strict, 
                         object_pairs_hook=object_pairs_hook)
        self.parse_object = self.object
        self.scan_once = py_make_scanner(self)
        
    def object(
        self, 
        s_and_end, 
        strict, scan_once, object_hook, object_pairs_hook, memo=None, _w=WHITESPACE.match, _ws=WHITESPACE_STR
    ) -> (NotebookNode, int):
        object, next = JSONObject(s_and_end, strict, scan_once, object_hook, object_pairs_hook, memo=memo, _w=_w, _ws=_ws)

        if 'cell_type' in object: 
            object['metadata'].update({
                'lineno':  len(s_and_end[0][:next].rsplit('"source":', 1)[0].splitlines())
            })
            
        for key in ('source', 'text'): 
            if key in object: object[key] = ''.join(object[key])
        return NotebookNode(object), next


# # Compilation
# 
# Compilation occurs in the __3__ steps:
# 
# 1. Text is transformed into a valid source string.
# 2. The source string is parsed into an abstract syntax tree
# 3. The abstract syntax compiles to valid bytecode 

# In[2]:


from IPython.core.compilerop import CachingCompiler
from dataclasses import dataclass, field

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


import ast, sys
from json import load, loads
from nbformat import NotebookNode, read, reads
from pathlib import Path
from nbconvert.exporters.markdown import MarkdownExporter
from nbconvert.exporters.notebook import NotebookExporter


# In[4]:


@dataclass
class Code(NotebookExporter, Compiler):
    """An exporter than returns transforms a NotebookNode through the InputSplitter.
    
    >>> assert type(Code().from_filename('compiler.ipynb')) is NotebookNode"""
    filename: str = '<module exporter>'
    name: str = '__main__'
    decoder: type = LineNoDecoder
        
    def __post_init__(self): NotebookExporter.__init__(self) or Compiler.__init__(self)
            
    def from_file(Code,file_stream, resources=None, **dict): 
        for str in ('name', 'filename'): setattr(Code, str, dict.pop(str, getattr(Code, str)))
        return Code.from_notebook_node(
            NotebookNode(**load(file_stream, cls=Code.decoder)), resources, **dict)
    
    def from_filename(Code,  filename, resources=None, **dict):
        Code.filename, Code.name = filename, Path(filename).stem
        return super().from_filename(filename, resources, **dict)

    def from_notebook_node(Code, nb, resources=None, **dict): 
        for cell in nb['cells']:
            if cell['cell_type'] == 'code':
                cell.source = Code.from_code_cell(cell, **dict)
        return nb
    
    def from_code_cell(Code, cell, **dict):  
        return Code.transform(cell['source'])


# In[5]:


class AST(Code):
    """An exporter than returns parsed ast.
    
    >>> assert type(AST().from_filename('compiler.ipynb')) is ast.Module"""
    def from_notebook_node(AST, nb: NotebookNode, resource: dict=None, **dict):         
        return AST.ast_transform(ast.fix_missing_locations(ast.Module(body=sum((
            AST.ast_parse(
                AST.from_code_cell(cell, **dict), lineno=cell['metadata'].get('lineno', 1)
            ).body for cell in nb.cells if cell['cell_type']=='code'
        ), []))))


# In[6]:


class Compile(AST):
    """An exporter that returns compiled and cached bytecode.
    
    >>> assert Compile().from_filename('compiler.ipynb')"""        
    def from_notebook_node(Compile, nb, resources: dict=None, **dict):
        return Compile.compile(super().from_notebook_node(nb, resources, **dict))


# In[7]:


if __name__ ==  '__main__':
    get_ipython().system('jupyter nbconvert --to script compiler.ipynb')
    __import__('doctest').testmod()


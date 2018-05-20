
# coding: utf-8

"""# The IPython compiler"""


try:
    from .decoder import load
except:
    from decoder import load

from nbconvert.exporters.python import PythonExporter as _PythonExporter
from nbconvert.exporters.notebook import NotebookExporter
from nbformat import from_dict
from IPython.core.compilerop import CachingCompiler
import ast


class Compiler(CachingCompiler):
    """{Shell} provides the IPython machinery to objects."""

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
    def transform(Compiler):
        return Compiler.ip.input_transformer_manager.transform_cell

    def compile(Compiler, ast):
        """Compile AST to bytecode using the an IPython compiler."""
        return (Compiler.ip and Compiler.ip.compile or CachingCompiler())(
            ast, Compiler.filename, "exec"
        )

    def ast_parse(Compiler, source, filename="<unknown>", symbol="exec", lineno=0):
        return ast.increment_lineno(super().ast_parse(source, Compiler.filename, "exec"), lineno)


class PythonExporter(_PythonExporter):

    def from_file(self, file_stream, resources=None, **kw):
        return self.from_notebook_node(from_dict(load(file_stream)), resources, **kw)


if __name__ == "__main__":
    try:
        from .compile import export
    except:
        from compile import export
    export("compile_ipython.ipynb", "../importnb/compile_ipython.py")
    __import__("doctest").testmod()

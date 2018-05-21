
# coding: utf-8

"""# The Python compile module
"""


import ast, sys

try:
    from .decoder import load
except:
    from decoder import load
from pathlib import Path
from textwrap import dedent
from codeop import Compile


class PythonCompiler(Compile):
    """{Shell} provides the IPython machinery to objects."""

    def ast_transform(Compiler, node):
        return node

    @property
    def transform(Compiler):
        return dedent

    def compile(Compiler, ast):
        return compile(ast, Compiler.filename, "exec")

    def ast_parse(Compiler, source, filename="<unknown>", symbol="exec", lineno=0):
        return ast.increment_lineno(ast.parse(source, Compiler.filename, "exec"), lineno)


Compiler = PythonCompiler


class PythonNotebookExporter:

    def from_file(self, file_stream, resources=None, **kw):
        return self.from_notebook_node(load(file_stream), resources, **kw)

    def from_filename(self, filename, resources=None, **dict):
        with open(filename, "r") as file_stream:
            return self.from_file(file_stream, resources, **dict)

    def from_notebook_node(self, nb, resources=None, **dict):
        return nb, resources


NotebookExporter = PythonNotebookExporter


class PythonPythonExporter(NotebookExporter):

    def from_notebook_node(self, nb, resources=None, **dict):
        nb, resources = super().from_notebook_node(nb, resources, **dict)
        for i, cell in enumerate(nb["cells"]):
            if isinstance(cell["source"], list):
                nb["cells"][i]["source"] = "".join(cell["source"])
        return ("\n" * 2).join(
            dedent(cell["source"]) for cell in nb["cells"] if cell["cell_type"] == "code"
        ), resources


PythonExporter = PythonPythonExporter


if __name__ == "__main__":
    try:
        from .compile import export
    except:
        from compile import export
    export("compile_python.ipynb", "../importnb/compile_python.py")
    __import__("doctest").testmod()

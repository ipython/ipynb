import ast, sys
from json import load, loads
from pathlib import Path
from textwrap import dedent

from codeop import Compile
from dataclasses import dataclass, field


class Compiler(Compile):
    """{Shell} provides the IPython machinery to objects."""
    filename: str = "<Shell>"

    def ast_transform(Compiler, node):
        return node

    @property
    def transform(Compiler):
        return dedent

    def compile(Compiler, ast):
        return compile(ast, Compiler.filename, "exec")

    def ast_parse(Compiler, source, filename="<unknown>", symbol="exec", lineno=0):
        return ast.increment_lineno(ast.parse(source, Compiler.filename, "exec"), lineno)


class NotebookExporter:

    def from_file(self, file_stream, resources=None, **dict):
        return self.from_notebook_node(load(file_stream), resources=resources, **dict)

    def from_filename(self, filename, resources=None, **dict):
        with open(filename, "r") as file_stream:
            return self.from_file(file_stream, resources, **dict)

    def from_notebook_node(self, nb, resources=None, **dict):
        return nb, resources


class ScriptExporter(NotebookExporter):

    def from_notebook_node(self, nb, resources=None, **dict):
        nb, resources = super().from_notebook_node(nb, resources, **dict)
        for i, cell in enumerate(nb["cells"]):
            if isinstance(cell["source"], list):
                nb["cells"][i]["source"] = "".join(cell["source"])

        return ("\n" * 2).join(
            dedent(cell["source"]) for cell in nb["cells"] if cell["cell_type"] == "code"
        ), resources


NotebookNode = dict

if __name__ == "__main__":
    from pathlib import Path

    Path("compiler_python.py").write_text(
        ScriptExporter().from_filename("compiler_python.ipynb")[0]
    )
    __import__("doctest").testmod()

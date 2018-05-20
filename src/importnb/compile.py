
# coding: utf-8
"""
# The `compile` module
"""

import ast, sys
from pathlib import Path

__file__ = globals().get("__file__", "compile.ipynb")
__nb__ = __file__.replace("src/importnb", "src/notebooks")


__IPYTHON__ = False

try:
    from IPython import get_ipython

    if not get_ipython():
        ...
    else:
        __IPYTHON__ = True
except:
    ...


if __IPYTHON__:
    try:
        from .compile_ipython import Compiler, PythonExporter, NotebookExporter, NotebookNode
    except:
        from compile_ipython import Compiler, PythonExporter, NotebookExporter, NotebookNode
    PythonExporter.template_path.default_args[0].append(str(Path(__file__).parent))
else:
    try:
        from .compile_python import Compiler, PythonExporter, NotebookExporter, NotebookNode
    except:
        from compile_python import Compiler, PythonExporter, NotebookExporter, NotebookNode
try:
    from .decoder import loads
except:
    from decoder import loads


class ImportNbStyleExporter(PythonExporter):
    template_file = "block_string.tpl"
    PythonExporter.exclude_input_prompt = True

    def from_notebook_node(self, nb, resources=None, **kw):
        code, resources = super().from_notebook_node(nb, resources=resources, **kw)
        try:
            from black import format_str
        except:
            format_str = lambda x, i: x
        return format_str(code, 100), resources


def export(file, to=None):
    from pathlib import Path

    exporter = ImportNbStyleExporter()
    code = exporter.from_filename(file)[0]
    if to:
        Path(to).with_suffix(exporter.file_extension).write_text(code)
    return code


def wrap_md_docstring(object):
    if isinstance(object, list):
        object = "".join(object)
    if '"""' in object:
        return "'''{}'''".format(object)
    return '"""{}"""'.format(object)


import sys


class Code(NotebookExporter, Compiler):
    """An exporter than returns transforms a NotebookNode through the InputSplitter.
    
    >>> assert type(Code().from_filename(Path(__nb__).with_suffix('.ipynb'))) is NotebookNode"""

    def __init__(self, filename="<module exporter>", name="__main__"):
        NotebookExporter.__init__(self)
        Compiler.__init__(self)
        self.filename = filename
        self.name = name

    def from_file(Code, file_stream, resources=None, **dict):
        for str in ("name", "filename"):
            setattr(Code, str, dict.pop(str, getattr(Code, str)))
        file_stream = file_stream.read()
        if isinstance(file_stream, bytes):
            file_stream = file_stream.decode("utf-8")
        return Code.from_notebook_node(NotebookNode(**loads(file_stream)), resources, **dict)

    def from_filename(Code, filename, resources=None, **dict):
        Code.filename, Code.name = filename, Path(filename).stem
        return super().from_filename(filename, resources, **dict)

    def from_notebook_node(Code, nb, resources=None, **dict):
        for index, cell in enumerate(nb["cells"]):
            if cell["cell_type"] == "markdown":
                cell.update(
                    source=["", "__doc__ = "][index == 0 and sys.version_info.minor >= 7]
                    + wrap_md_docstring(cell["source"]),
                    cell_type="code",
                )
            if cell["cell_type"] == "code":
                if isinstance(cell["source"], list):
                    cell["source"] = "".join(cell["source"])
                cell["source"] = Code.from_code_cell(cell, **dict)
        return nb

    def from_code_cell(Code, cell, **dict):
        return Code.transform(cell["source"])


class AST(Code):
    """An exporter than returns parsed ast.
    
    >>> assert type(AST().from_filename(Path(__nb__).with_suffix('.ipynb'))) is ast.Module"""

    def from_notebook_node(AST, nb, resource=None, **dict):
        return AST.ast_transform(
            ast.fix_missing_locations(
                ast.Module(
                    body=sum(
                        (
                            AST.ast_parse(
                                AST.from_code_cell(cell, **dict),
                                lineno=cell["metadata"].get("lineno", 1),
                            ).body
                            for cell in super().from_notebook_node(nb, resource, **dict)["cells"]
                            if cell["cell_type"] == "code"
                        ),
                        [],
                    )
                )
            )
        )


class Compile(AST):
    """An exporter that returns compiled and cached bytecode.
    
    >>> assert Compile().from_filename(Path(__nb__).with_suffix('.ipynb'))"""

    def from_notebook_node(Compile, nb, resources: dict = None, **dict):
        return Compile.compile(super().from_notebook_node(nb, resources, **dict))


if __name__ == "__main__":
    export("compile.ipynb", "../importnb/compile.py")
    __import__("doctest").testmod()
    print(__import__("compile").__doc__)

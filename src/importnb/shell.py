# coding: utf-8
"""# The Shell Mixin

Allows the current ipython configuration to effect the code and ast tranformers.
"""

try:
    from IPython.core.inputsplitter import IPythonInputSplitter

    dedent = IPythonInputSplitter().transform_cell
except:
    from textwrap import dedent


class ShellMixin:

    @property
    def _shell(self):
        try:
            return __import__("IPython").get_ipython()
        except:
            return

    def format(self, str):
        return (self._shell and self._shell.input_transformer_manager.transform_cell or dedent)(str)

    def visit(self, node):
        if self._shell:
            for visitor in self._shell.ast_transformers:
                node = visitor.visit(node)
        return node


if __name__ == "__main__":
    from importnb.utils.export import export

    export("shell.ipynb", "../shell.py")

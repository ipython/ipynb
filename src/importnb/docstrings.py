# coding: utf-8
"""# Special handling of markdown cells as docstrings.
"""

import ast


def update_docstring(module):
    from functools import reduce

    module.body = reduce(markdown_docstring, module.body, [])
    return module


def markdown_docstring(nodes, node):
    if (
        len(nodes) > 1
        and str_expr(nodes[-1])
        and isinstance(node, (ast.ClassDef, ast.FunctionDef))
        and not str_expr(node.body[0])
    ):
        node.body.insert(0, nodes.pop())
    return nodes.append(node) or nodes


def str_expr(node):
    return isinstance(node, ast.Expr) and isinstance(node.value, ast.Str)


if __name__ == "__main__":
    try:
        from utils.export import export
    except:
        from .utils.export import export
    export("docstrings.ipynb", "../docstrings.py")

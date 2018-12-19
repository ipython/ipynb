# coding: utf-8
"""# Special handling of markdown cells as docstrings.

Modify the Python `ast` to assign docstrings to functions when they are preceded by a Markdown cell.
"""

import ast

"""# Modifying the `ast`

    >>> assert isinstance(create_test, ast.Assign)
    >>> assert isinstance(test_update, ast.Attribute)
"""

create_test = ast.parse("""__test__ = globals().get('__test__', {})""", mode="single").body[0]
test_update = ast.parse("""__test__.update""", mode="single").body[0].value
str_nodes = (ast.Str,)

try:
    str_nodes += (ast.JoinedStr,)
except:
    ...

"""`TestStrings` is an `ast.NodeTransformer` that captures `str_nodes` in the `TestStrings.strings` object.

```ipython
>>> assert isinstance(ast.parse(TestStrings().visit(ast.parse('"Test me"'))), ast.Module)

```
"""


class TestStrings(ast.NodeTransformer):

    strings = None

    def visit_Module(self, module):
        """`TestStrings.visit_Module` initializes the capture. After all the nodes are visit we append `create_test and test_update`
        to populate the `"__test__"` attribute.
        """
        self.strings = []
        module = self.visit_body(module)
        module.body += (
            [create_test]
            + [
                ast.copy_location(
                    ast.Expr(
                        ast.Call(
                            func=test_update,
                            args=[
                                ast.Dict(
                                    keys=[ast.Str("string-{}".format(node.lineno))], values=[node]
                                )
                            ],
                            keywords=[],
                        )
                    ),
                    node,
                )
                for node in self.strings
            ]
            if self.strings
            else []
        )
        return module

    def visit_body(self, node):
        """`TestStrings.visit_body` visits nodes with a `"body"` attibute and extracts potential string tests."""

        body = []
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, str_nodes)
        ):
            body.append(node.body.pop(0))
        node.body = body + [
            (self.visit_body if hasattr(object, "body") else self.visit)(object)
            for object in node.body
        ]
        return node

    def visit_Expr(self, node):
        """`TestStrings.visit_Expr` append the `str_nodes` to `TestStrings.strings` to append to the `ast.Module`."""

        if isinstance(node.value, str_nodes):
            self.strings.append(
                ast.copy_location(ast.Str(node.value.s.replace("\n```", "\n")), node)
            )
        return node


def update_docstring(module):
    from functools import reduce

    module.body = reduce(markdown_docstring, module.body, [])
    return TestStrings().visit(module)


docstring_ast_types = ast.ClassDef, ast.FunctionDef
try:
    docstring_ast_types += (ast.AsyncFunctionDef,)
except:
    ...


def markdown_docstring(nodes, node):
    if (
        len(nodes) > 1
        and str_expr(nodes[-1])
        and isinstance(node, docstring_ast_types)
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

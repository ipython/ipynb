# coding: utf-8
"""An ast node transformer to allow relative imports in the notebook.

This is generally meant to be used in the main context.

    > %load_ext importnb.utils.relative
    >>> if __name__ == '__main__':
    ...     from .__tive import RelativeImport
"""

import ast


class RelativeImport(ast.NodeTransformer):
    def visit_Try(self, node):
        return node

    visit_ClassDef = visit_FuntionDef = visit_Try

    def visit_ImportFrom(self, node):
        if node.level == 1:
            if node.module:
                next = ast.ImportFrom(node.module, node.names, 0)
            else:
                next = ast.Import(node.names)

            node = ast.copy_location(
                ast.Try(
                    [node], [ast.ExceptHandler(None, None, [ast.copy_location(next, node)])], [], []
                ),
                node,
            )

        return node


def load_ipython_extension(ip=None):
    if ip:
        unload_ipython_extension(ip)
        ip.ast_transformers += [RelativeImport()]


def unload_ipython_extension(ip):
    if ip:
        ip.ast_transformers = [
            object for object in ip.ast_transformers if not isinstance(object, RelativeImport)
        ]


if __name__ == "__main__":
    from importnb.utils.export import export

    export("relative.ipynb", "../../utils/relative.py")

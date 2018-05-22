
# coding: utf-8

try:
    from .loader import Notebook
    from .decoder import loads_ast
except:
    from loader import Notebook
    from decoder import loads_ast
from inspect import getsource

from types import ModuleType


"""Are single target `ast.Expr` that will `ast.literal_eval` is a possible parameter.
"""


from ast import (
    NodeTransformer,
    parse,
    Assign,
    literal_eval,
    dump,
    fix_missing_locations,
    Str,
    Tuple,
)


class FreeStatementFinder(NodeTransformer):

    def __init__(self, params=None, globals=None):
        self.params = params if params is not None else []
        self.globals = globals if globals is not None else {}

    visit_Module = NodeTransformer.generic_visit

    def visit_Assign(FreeStatement, node):
        if len(node.targets):
            try:
                if not getattr(node.targets[0], "id", "_").startswith("_"):
                    FreeStatement.globals[node.targets[0].id] = literal_eval(node.value)
                    return
            except:
                assert True, """The target can not will not literally evaluate."""
        return node

    def generic_visit(self, node):
        return node

    def __call__(FreeStatement, nodes):
        return FreeStatement.globals, fix_missing_locations(FreeStatement.visit(nodes))


"""# `Parameterize` notebooks

`Parameterize` is callable version of a notebook.  It uses `pidgin` to load the `NotebookNode` and evaluates the `FreeStatement`s to discover the signature.
"""


class Parameterize:
    """Parameterize takes a module, filename, or notebook dictionary and returns callable object that parameterizes the notebook module.
    
    f = Parameterize('parameterize.ipynb')
    """

    def __init__(self, object=None):
        from importnb.capture import capture_output
        from pathlib import Path
        from json import load, loads

        self.object = object

        self.__file__ = None

        if isinstance(object, ModuleType):
            self.__file__ = object.__file__
            object = getsource(object)
        elif isinstance(object, (Path, str)):
            self.__file__ = object
            with open(str(object)) as f:
                object = f.read()
        elif isinstance(object, dict):
            ...
        else:
            raise ValueError("object must be a module, file string, or dict.")

        self.__variables__, self.__ast__ = FreeStatementFinder()(loads_ast(object))
        self.__signature__ = self.vars_to_sig(**self.__variables__)

    def __call__(self, **dict):
        self = __import__("copy").copy(self)
        self.__dict__.update(self.__variables__)
        self.__dict__.update(dict)
        exec(
            compile(self.__ast__, self.__file__ or "<parameterized>", "exec"), *[self.__dict__] * 2
        )
        return self

    def interact(Parameterize):
        """Use the ipywidgets.interact to explore the parameterized notebook."""
        return __import__("ipywidgets").interact(Parameterize)

    @staticmethod
    def vars_to_sig(**vars):
        """Create a signature for a dictionary of names."""
        from inspect import Parameter, Signature

        return Signature(
            [Parameter(str, Parameter.KEYWORD_ONLY, default=vars[str]) for str in vars]
        )


"""#### Examples that do work
"""


import sys

param = "xyz"
extraparam = 42


"""#### Examples that do *not* work
"""


"""Parameters are not created when literal_eval fails."""
noparam0 = Parameterize

"""Multiple target assignments are ignored."""
noparam1, noparam2 = "xyz", 42


"""## Developer
"""


__test__ = dict(
    imports="""
    >>> assert callable(f)
    """,
    default="""
    >>> default = f()
    >>> assert default.param == default.noparam1 == 'xyz' and default.noparam2 == 42
    >>> assert all(str not in default.__signature__.parameters for str in ('noparam', 'noparam1', 'noparam2'))
    """,
    reuse="""
    >>> new = f(param=10)
    >>> assert new.param is 10 and new.extraparam is 42""",
)
if __name__ == "__main__":
    f = Parameterize(globals().get("__file__", "parameterize.ipynb"))
    __import__("doctest").testmod(verbose=1)


if __name__ == "__main__":
    #         export('parameterize.ipynb', '../parameterize.py')
    __import__("doctest").testmod()

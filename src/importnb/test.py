# coding: utf-8
"""# Notebook testing loaders and notebook unittests

    >>> assert inspect.signature(main) == inspect.signature(_main)
    >>> assert inspect.getdoc(main) == inspect.getdoc(_main)
"""

from unittest import main as _main, TestCase
from types import ModuleType
import sys, inspect, copy

__file__ = globals().get("__file__", None)


def attach_doctest(module):
    """A function to include doctests in a unittest suite.
    """
    from doctest import DocTestSuite

    def load_tests(loader, tests, ignore):
        tests.addTests(DocTestSuite(module))
        return tests

    module.load_tests = load_tests
    return module


try:
    from .loader import Notebook
except:
    from loader import Notebook


class DoctestModule(Notebook):

    def exec_module(self, module, **kwargs):
        super().exec_module(module)


class UnittestModule(Notebook):

    def exec_module(self, module, **kwargs):
        super().exec_module(module)
        _main(module=module, argv=module.__file__.split())


def main(module=None, *args, doctest=True, exit=False, argv="--doctest", **dict):
    """In interactive mode we do not want to raise SystemExit"""

    dict.update(exit=exit, argv=argv)

    loader = Notebook

    if sys.argv[0] == __file__:
        argv = sys.argv
    else:
        if isinstance(argv, str):
            argv = argv.split()
        if "discover" not in argv:
            argv = ["discover"] + argv

    if "--doctest" in argv:
        argv.pop(argv.index("--doctest"))
        doctest = True

    if doctest:
        if isinstance(module, ModuleType):
            attach_doctest(module)
        else:
            loader = DoctestModule

    dict.update(argv=argv)

    with loader():
        _main(module, *args, **dict)


main.__signature__ = inspect.signature(_main)
main.__doc__ = inspect.getdoc(_main)


class AUnitTestExample(TestCase):

    def test_this(self):
        assert True


if __name__ == "__main__":
    if sys.argv[0] == __file__:
        main(module=None, exit=True, argv=None)
    else:
        try:
            from .utils.export import export
        except:
            from utils.export import export
        export("test.ipynb", "../test.py")
        module = Notebook().from_filename("test.ipynb", "importnb.notebooks")
        main(module)

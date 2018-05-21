
# coding: utf-8

"""# Load and test notebooks

New ideas may include tests in a notebook.  The `importnb.test.Test` context will `doctest` and `unittest` a notebook.

    >>> from importnb import NotebookTest
    >>> assert NotebookTest
"""


try:
    from .loader import Notebook, export
except:
    from loader import Notebook, export

from unittest import TestProgram, TestCase
from doctest import DocTestSuite

__file__ = globals().get("__file__", "nbtest.ipynb")


def attach_doctest(module):
    """A function to include doctests in a unittest suite.
    """

    def load_tests(loader, tests, ignore):
        tests.addTests(DocTestSuite(module))
        return tests

    module.load_tests = load_tests
    return module


def testmod(
    module, extras="", doctest=True, exit=True, verbosity=1, failfast=None, catchbreak=None
):
    """Test a module using unittest, include the docstrings by default."""
    if doctest:
        attach_doctest(module)
    try:
        TestProgram(
            module,
            argv=" ".join(("discover", extras)).split(),
            exit=exit,
            verbosity=verbosity,
            failfast=failfast,
            catchbreak=catchbreak,
        )
    except SystemExit:
        ...
    return module


class NotebookTest(Notebook):

    def exec_module(self, module):
        super().exec_module(module)
        testmod(module)


class _test(TestCase):

    def test_importnb_test(self):
        assert True


if __name__ == "__main__":
    export("nbtest.ipynb", "../importnb/nbtest.py")
    __import__("doctest").testmod(Notebook.from_filename("nbtest.ipynb"))
    m = NotebookTest.from_filename(__file__)
    testmod(m, "-f")

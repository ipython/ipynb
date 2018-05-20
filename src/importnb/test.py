
# coding: utf-8

"""# Load and test notebooks

New ideas may include tests in a notebook.  The `importnb.test.Test` context will `doctest` and `unittest` a notebook.
"""


try:
    from .loader import Notebook, export
except:
    from loader import Notebook, export

from unittest import TestProgram, TestCase
from doctest import DocTestSuite

__file__ = globals().get("__file__", "test.ipynb")


def attach_doctest(module):

    def load_tests(loader, tests, ignore):
        tests.addTests(DocTestSuite(module))
        return tests

    module.load_tests = load_tests
    return module


class Test(Notebook):

    def exec_module(self, module):
        super().exec_module(module)
        attach_doctest(module)
        try:
            TestProgram(module, argv="discover".split())
        except SystemExit:
            ...
        return module


class _test(TestCase):

    def test_importnb_test(self):
        assert False


if __name__ == "__main__":
    export("test.ipynb", "../importnb/test.py")
    __import__("doctest").testmod(Notebook.from_filename("loader.ipynb"))
    m = Test.from_filename(__file__)

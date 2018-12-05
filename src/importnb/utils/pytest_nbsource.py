# coding: utf-8
"""`pytest_nbsource` sets some rules when notebooks are used as source code.
"""

with __import__("importnb").Notebook():
    try:
        from . import testing
    except:
        from importnb.utils import testing

import importlib, pytest, abc, pathlib

from importnb import Notebook


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption(
        "--nbsource",
        action="store_true",
        help="""Notebook source code has monotonically increasing execution result
values and a leading Markdown string is the docstring.""",
    )


def pytest_collect_file(parent, path):
    """`pytest_collect_file` will collect notebooks."""

    if path.ext == ".ipynb":
        return NotebookFile(path, parent)


class NotebookFile(pytest.File):
    def collect(self):
        nb = __import__("json").load(self.fspath.open())
        if self.parent.config.option.nbsource:
            yield AggregateNotebookTests(
                testing.assert_execution_order.__name__, self, nb, testing.assert_execution_order
            )
            yield AggregateNotebookTests(
                testing.assert_markdown_docstring.__name__,
                self,
                nb,
                testing.assert_markdown_docstring,
            )


class AggregateNotebookTests(pytest.Item):
    """`AggregateNotebookTests` is a `pytest.Item` for testing features of notebook data."""

    def runtest(self):
        return self.callable(self.nb)

    def __init__(self, name, parent, nb, callable):
        super().__init__(name, parent)
        self.nb, self.callable = nb, callable

    def reportinfo(self):
        """`AggregateNotebookTests.repr_failure` is really similar the to the <b><i>render_traceback</i></b> attribute provided by `IPython` to customize tracebacks."""
        return self.fspath, 0, "usecase: %s" % self.name


if __name__ == "__main__":
    from importnb.utils.export import export

    export("pytest_nbsource.ipynb", "../../utils/pytest_nbsource.py")

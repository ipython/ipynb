# coding: utf-8
"""A `pytest` plugin for importing notebooks as modules and using standard test discovered.

The `AlternativeModule` is reusable.  See `pidgin` for an example.
"""

from importnb import Notebook

import importlib, pytest, abc, pathlib, _pytest, functools


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption("--main", action="store_true", help="Run in the main context.")
    group.addoption(
        "--monotonic",
        action="store_true",
        help="""Notebook source code has monotonically increasing execution result
values and a leading Markdown string is the docstring.""",
    )


"""`assert_execution_order` are the notebook outputs monotonically increasing.  This assists in more consistent state.
"""


def assert_execution_order(nb, file=None):
    shift = 1
    for id, object in enumerate(object for object in nb["cells"] if object["cell_type"] == "code"):
        id += shift
        source = "".join(object["source"])
        if object["execution_count"] is None:
            assert (
                not source.strip()
            ), """{file} has an unexecuted with the source:\n{source}.""".format(
                **locals()
            )
            shift -= 1
        else:
            assert (
                object["execution_count"] == id
            ), """{file} has been executed out of order.""".format(**locals())

    return True


"""`MonotonicExecution` wiil `assert_execution_order`  of a notebook.
"""


class MonotonicExecution(pytest.File):
    def collect(self):
        nb = __import__("json").load(self.fspath.open())
        yield _pytest.python.Function(
            assert_execution_order.__name__,
            self,
            callobj=functools.partial(assert_execution_order, nb, file=self.fspath),
        )


"""`AlternativeModule` is an alternative `pytest.Module` loader that can enable `pytest.Doctest`.
"""


class AlternativeModule(pytest.Module):
    def _getobj(self):
        return self.loader(
            getattr(self.parent.config.option, "main", None) and "__main__" or None
        ).load(str(self.fspath))

    def collect(self):
        if self.parent.config.option.monotonic and self.fspath.ext == ".ipynb":
            yield from MonotonicExecution.collect(self)
        yield from super().collect()
        if self.parent.config.option.doctestmodules:
            self.fspath.pyimport = functools.partial(
                self.fspath.pyimport, modname=self._obj.__name__
            )
            yield from _pytest.doctest.DoctestModule.collect(self)


"""`NotebookModule` is an `AlternativeModule` to load `Notebook`s.
"""


class NotebookModule(AlternativeModule):
    loader = Notebook


class AlternativeSourceText(abc.ABCMeta):
    def __call__(self, parent, path):
        for module in self.modules:
            if "".join(pathlib.Path(str(path)).suffixes) in module.loader.extensions:
                if not parent.session.isinitpath(path):
                    for pat in parent.config.getini("python_files"):
                        if path.fnmatch(pat.rstrip(".py") + path.ext):
                            break
                    else:
                        return
                return module(path, parent)


class NotebookTests(metaclass=AlternativeSourceText):
    modules = (NotebookModule,)


pytest_collect_file = NotebookTests.__call__

if __name__ == "__main__":
    from importnb.utils.export import export

    export("pytest_importnb.ipynb", "../../utils/pytest_importnb.py")

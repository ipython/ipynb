# coding: utf-8
"""A `pytest` plugin for importing notebooks as modules and using standard test discovered.

The `AlternativeModule` is reusable.  See `pidgin` for an example.
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
    group.addoption("--main", action="store_true", help="Run in the main context.")


import _pytest.doctest


class AlternativeModule(pytest.Module):
    def _getobj(self):
        return self.loader(self.parent.config.option.main and "__main__" or None).load(
            str(self.fspath)
        )

    def collect(self):
        yield from super().collect()
        if self.parent.config.option.doctestmodules:
            yield from _pytest.doctest.DoctestModule.collect(self)


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

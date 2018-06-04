# coding: utf-8
import pytest

try:
    from ..loader import Notebook
except:
    from importnb.loader import Notebook

loader = Notebook


def pytest_collect_file(parent, path):
    if path.ext in (".ipynb", ".py"):
        if not parent.session.isinitpath(path):
            for pat in parent.config.getini("python_files"):
                if path.fnmatch(pat.rstrip(".py") + path.ext):
                    break
            else:
                return
        return PytestModule(path, parent)


class PytestModule(pytest.Module):

    def collect(self):
        global loader
        with loader():
            return super().collect()


if __name__ == "__main__":
    from importnb.utils.export import export

    export("pytest_plugin.ipynb", "../../utils/pytest_plugin.py")

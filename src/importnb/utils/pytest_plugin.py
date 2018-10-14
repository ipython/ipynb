# coding: utf-8
import pytest

try:
    from .. import Notebook
except:
    from importnb import Notebook
from pathlib import Path

loader = Notebook


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption(
        "--shell", action="store_false", help="Load notebooks with a shared transformer."
    )
    group.addoption("--main", action="store_true", help="Run in the main context.")


def pytest_collect_file(parent, path):
    if "".join(Path(str(path)).suffixes) in (".ipynb",):
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
        with loader(
            self.parent.config.option.main and "__main__" or None,
            shell=self.parent.config.option.shell,
        ):
            return super().collect()


if __name__ == "__main__":
    from importnb.utils.export import export

    export("pytest_plugin.ipynb", "../../utils/pytest_plugin.py")

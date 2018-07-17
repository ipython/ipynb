# coding: utf-8
import pytest

try:
    from .. import Interactive
except:
    from importnb import Interactive

loader = Interactive


def pytest_addoption(parser):
    """
    Adds the --nbval option flag for py.test.
    Adds an optional flag to pass a config file with regex
    expressions to sanitise the outputs
    Only will work if the --nbval flag is present
    This is called by the pytest API
    """
    group = parser.getgroup("general")
    group.addoption(
        "--shell", action="store_false", help="Load notebooks with a shared transformer."
    )
    group.addoption("--main", action="store_true", help="Run in the main context.")


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
        with loader(
            self.parent.config.option.main and "__main__" or None,
            shell=self.parent.config.option.shell,
        ):
            return super().collect()


if __name__ == "__main__":
    from importnb.utils.export import export

    export("pytest_plugin.ipynb", "../../utils/pytest_plugin.py")

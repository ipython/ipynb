import pytest

try:
    from .loader import Notebook
except:
    from loader import Notebook


def pytest_collect_file(parent, path):
    if path.ext in (".ipynb", ".py"):
        return Module(path, parent)


class Module(pytest.Module):

    def collect(self):
        with Notebook():
            return super().collect()


if __name__ == "__main__":
    try:
        from .compiler_python import ScriptExporter
    except:
        from compiler_python import ScriptExporter
    from pathlib import Path

    Path("test.py").write_text(ScriptExporter().from_filename("test.ipynb")[0])

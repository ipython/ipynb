__IPYTHON__ = False

try:
    from IPython import get_ipython

    if not get_ipython():
        ...
    else:
        __IPYTHON__ = True
except:
    ...

from pathlib import Path

try:
    from ..compiler_python import ScriptExporter
except:
    from importnb.compiler_python import ScriptExporter


def export(src, dst, columns=100):
    try:
        from black import format_str
    except:
        format_str = lambda str, int: str
    Path(dst).write_text(format_str(ScriptExporter().from_filename(src)[0], columns))


if __name__ == "__main__":
    export("__init__.ipynb", "../../importnb/utils/__init__.py")
    export("__init__.ipynb", "__init__.py")

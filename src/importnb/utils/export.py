# coding: utf-8
"""# The `export` module

...provides compatibility for Python and IPython through [`compile_python`](compile_python.ipynb) and [`compile_ipython`](compile_ipython.ipynb), respectively.  

    >>> from importnb.utils.export import export
"""

try:
    from ..loader import dedent
except:
    from importnb.loader import dedent
from pathlib import Path

try:
    from black import format_str
except:
    format_str = lambda x, i: x
from json import loads


def block_str(str):
    quotes = '"""'
    if quotes in str:
        quotes = "'''"
    return "{quotes}{str}\n{quotes}\n".format(quotes=quotes, str=str)


"""The export function
"""


def export(file, to=None):
    code = """# coding: utf-8"""
    with open(str(file), "r") as f:
        for cell in loads(f.read())["cells"]:
            if cell["cell_type"] == "markdown":
                code += "\n" + block_str("".join(cell["source"]))
            elif cell["cell_type"] == "code":
                code += "\n" + dedent("".join(cell["source"]))
    to and Path(to).with_suffix(".py").write_text(format_str(code, 100))
    return code


if __name__ == "__main__":
    export("export.ipynb", "../../utils/export.py")
    try:
        import export as this
    except:
        from . import export as this
    __import__("doctest").testmod(this, verbose=2)

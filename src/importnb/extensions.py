# coding: utf-8
"""# Jupyter magic extensions
"""

"""    %importnb --stdout --stderr --display --shell
"""

import argparse
from importlib import import_module


def get_module_object(str):
    module, object = str.split(":", 1)
    return getattr(import_module(module), object)


parser = argparse.ArgumentParser(description="""Define the importnb loader properties.""")
parser.add_argument("--stdout", action="store_false")
parser.add_argument("--stderr", action="store_false")
parser.add_argument("--display", action="store_false")
parser.add_argument("--cls", type=get_module_object, default="importnb.Notebook")
parser.add_argument("--fuzzy", action="store_true")

"""    parser.parse_args("--stdout --cls importnb.execute:Execute".split())
"""

try:
    from IPython.core import magic_arguments
    from IPython.core.magic import Magics, magics_class, line_magic, cell_magic, line_cell_magic

    __IPYTHON__ = True
except:
    __IPYTHON__ = False

if __IPYTHON__:

    @magics_class
    class ImportNbExtension(Magics):

        def __init__(self, shell):
            super().__init__(shell)

        @line_magic
        def importnb(self, line):
            args = parser.parse_args(line.split())
            return line

        @cell_magic
        def cmagic(self, line, cell):
            eval()
            return line, cell

        @line_cell_magic
        def lcmagic(self, line, cell=None):
            "Magic that works both as %lcmagic and as %%lcmagic"
            if cell is None:
                print("Called as line magic")
                return line
            else:
                print("Called as cell magic")
                return line, cell


def load_ipython_extension(ip=None):
    from .loader import Notebook

    loader = Notebook(shell=True)
    if ip:
        ip.register_magics(ImportNbExtension)
    loader.__enter__()


def unload_ipython_extension(ip=None):
    from .loader import Notebook

    Notebook(shell=True).__exit__(None, None, None)


"""# Developer
"""

if __name__ == "__main__":
    try:
        from utils.export import export
    except:
        from .utils.export import export
    export("extensions.ipynb", "../extensions.py")
    # m = Notebook(shell=True).from_filename('extensions.ipynb')
    # print(__import__('doctest').testmod(m, verbose=2))

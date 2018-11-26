# coding: utf-8
"""# `importnb` Jupyter magic extensions
"""

"""    %importnb --stdout --stderr --display --shell
"""

import argparse
from importlib import import_module
from functools import partial
import pkg_resources, inspect


def get_module_object(str):
    module, object = str.split(":", 1)
    return getattr(import_module(module), object)


parser = argparse.ArgumentParser(description="""Define the importnb loader properties.""")
parser.add_argument("--cls", type=get_module_object, default="importnb:Notebook")
parser.add_argument("--fuzzy", action="store_true")

try:
    from IPython.core import magic_arguments
    from IPython.core.magic import Magics, magics_class, line_magic, cell_magic, line_cell_magic

    __IPYTHON__ = True
except:
    __IPYTHON__ = False


class ImportNbExtensionBase:
    loaders = None

    def __init__(self, shell, loader=None):
        self.loaders = []
        # A default loader to install
        if loader:
            self.loaders.append(loader(position=-1).__enter__())


if __IPYTHON__:

    @magics_class
    class ImportNbExtension(Magics, ImportNbExtensionBase):
        loaders = None

        def __init__(self, shell, loader=None):
            Magics.__init__(self, shell)
            ImportNbExtensionBase.__init__(self, shell, loader)

        @line_cell_magic
        def importnb(self, line, cell=None):
            if line.strip() == "pop":
                return self.pop()

            details = vars(parser.parse_args(line.split()))
            self.loaders.append(details.pop("cls")(**details))

            if cell is None:
                self.loaders[-1].__enter__()
                return

            with self.loaders.pop(-1):
                self.parent.run_cell(cell)

        def unload(self):
            while self.loaders:
                self.pop()

        def pop(self):
            self.loaders.pop().__exit__(None, None, None)


else:

    class ImportNbExtension(ImportNbExtensionBase):
        ...


manager = None


def IPYTHON_MAIN():
    """Decide if the Ipython command line is running code."""
    import pkg_resources

    runner_frame = inspect.getouterframes(inspect.currentframe())[-2]
    return (
        getattr(runner_frame, "function", None)
        == pkg_resources.load_entry_point("ipython", "console_scripts", "ipython").__name__
    )


def load_ipython_extension(ip=None):
    global manager, module
    if IPYTHON_MAIN():
        from .parameterize import Parameterize as Notebook
    else:
        from .loader import Notebook

    # Auto loading only works in IPython and
    # we only read need it when there are parameters.
    manager = ImportNbExtension(ip, Notebook)

    if ip:
        ip.register_magics(manager)
        ip.user_ns.update(__path__=[str(__import__("pathlib").Path().absolute())])
        from .completer import load_ipython_extension

        load_ipython_extension(ip)

        ip.user_ns["reload"] = __import__("importlib").reload


def unload_ipython_extension(ip=None):
    global manager
    ip and manager and manager.unload()


"""# Developer
"""

if __name__ == "__main__":
    from importnb.utils.export import export

    export("ipython_extension.ipynb", "../ipython_extension.py")
    # m = Notebook(shell=True).from_filename('extensions.ipynb')
    # print(__import__('doctest').testmod(m, verbose=2))

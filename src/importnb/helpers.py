# coding: utf-8
"""# Constants to discover where a statement is executed from

> _These operators are experimental._

I hate `__name__ == '__main__'`, it throws people off.  Like Y the F R U doing that.

This notebook creates exports three objects that will tell if:

* If the statement was called from a `__main__` module.
* If the statement was called interactively.
* If the statement was called on an imported object.
"""

__all__ = "MAIN", "INTERACTIVE", "IMPORTED", "CLI"

from inspect import currentframe, getouterframes
from pathlib import Path
from abc import ABCMeta, abstractmethod

"""Get the current frame and retreive the first frame called outside of the defining class.  We are basically counting a set of known frames before the caller is found.
"""


def getframeinfo(object):
    if __import__("sys").version_info.minor == 4:
        return object[0]
    return object.frame


class state(metaclass=ABCMeta):
    """Base class for the state objects."""

    def __init__(self, id=0):
        self.id = id

    def _retrieve_frames(self):
        return [getframeinfo(object) for object in getouterframes(currentframe())]

    def _retrieve_caller_frame(self):
        """Frames in stack
        
        other calls frame calls bool calls 
        retrieve_caller_frame calls retrieve_frames 
        """
        (retrieve_caller, retrieve_frames, __bool__, *frames) = self._retrieve_frames()
        return frames[self.id]

    @abstractmethod
    def format(self):
        raise NotImplemented()

    def __bool__(self):
        frame = self._retrieve_caller_frame()
        return self.format(frame)


"""## Does `__name__ == '__main__'`?

The most common logic circuit.  It is annoying to type, ugly to read, and must go away.
"""


class main(state):
    """Use MAIN to discover if a statement is invoked as a __main__ program.

    replaces

        __name__ == '__main__'"""

    def format(self, frame):
        name = frame.f_globals.get("__name__")
        return name == "__main__"


MAIN = main()

"""## Is the module being run from the command line as an application?
"""


class cli(state):
    """Use CLI to discover if a statement is invoked as a __main__ program.

    replaces

        __name__ == '__main__' and __import__('sys').argv == __file__
    """

    def format(self, frame):
        name = frame.f_globals.get("__name__")
        file = frame.f_globals.get("__file__", None)
        return name == "__main__" and file == __import__("sys").argv[0]


CLI = cli()

"""## Is the code executed by IPython or Jupyter?
"""


class interactive(state):
    """Use INTERACTIVE to discover if a statement is invoked from IPython or Jupyter.

    replaces

        __name__ == '__main__' and globals().get('__file__', None) == None
    """

    def format(self, frame):
        name = frame.f_globals.get("__name__")
        file = frame.f_globals.get("__file__", None)
        return name == "__main__" and file is None


INTERACTIVE = interactive()

"""## Is the module simply being imported?
"""


class imported(state):
    """Use IMPORTED to discover if a statement is invoked as an imported module.

    replaces: 

        __name__ != '__main__'
    """

    def format(self, frame):
        name = frame.f_globals.get("__name__")
        return name != "__main__"


IMPORTED = imported()

"""## Magics

The magics will be called from a different frame depth.  These functions below access the proper frame.  This magic makes it possible to wrap logic around other magics.    
"""


def _main(line, cell):
    main(2) and get_ipython().run_cell(cell)


def _cli(line, cell):
    cli(2) and get_ipython().run_cell(cell)


def _interactive(line, cell):
    interactive(2) and get_ipython().run_cell(cell)


def _imported(line, cell):
    imported(2) and get_ipython().run_cell(cell)


def load_ipython_extension(ip=None):
    if ip:
        for object in (_main, _cli, _interactive, _imported):
            ip.register_magic_function(
                object, "cell", object.__name__.rsplit(".", 1)[-1].lstrip("_").upper()
            )


"""# Developer
"""


def test_imported():
    assert IMPORTED, "the logic is borked."
    assert not any((MAIN, INTERACTIVE, CLI))


if INTERACTIVE:
    __import__("pytest").main("-s helpers.ipynb".split())

if MAIN:
    from importnb.utils.export import export

    export("helpers.ipynb", "../helpers.py")

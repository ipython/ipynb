
# coding: utf-8

__all__ = "Notebook", "reload", "Parameterize", "Execute", "Interactive"

from .loader import (
    Notebook,
    unload_ipython_extension,
    reload,
)
from .execute import Execute, Interactive
from .parameterize import Parameterize
from .remote import remote
from . import test

def load_ipython_extension(ip):
    from .loader import load_ipython_extension
    load_ipython_extension(ip)
    from .utils.relative import load_ipython_extension
    load_ipython_extension(ip)
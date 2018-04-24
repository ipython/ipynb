from importnb import Notebook

with Notebook():
    try:
        from .unittests import *
    except:
        from unittests import *
from importnb import load_ipython_extension
load_ipython_extension()
try:
    from .unittests import *
except:
    from unittests import *
with __import__('importnb').Notebook():
    try:
        from .test import *
    except:
        from test import *
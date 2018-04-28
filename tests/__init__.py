with __import__('importnb').Notebook():
    try:
        from .test_ import *
    except:
        from test_ import *
with __import__('importnb').Notebook():
    try:
        from .test_unittests import *
    except:
        from test_unittests import *

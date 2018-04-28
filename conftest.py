try:
    from IPython import get_ipython
    assert get_ipython()
except:
    collect_ignore = ["importnb/compiler_ipython.py"]

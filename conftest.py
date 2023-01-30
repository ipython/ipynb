try:
    from IPython import get_ipython
    assert get_ipython()
except:
    collect_ignore = [
        "src/importnb/utils/ipython.py",
        "src/importnb/completer.py"
    ]

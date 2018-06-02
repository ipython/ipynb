collect_ignore = [
    "benchmarks",
    "src/importnb/test.py",
    "src/importnb/notebooks/test.ipynb"
]
try:
    from IPython import get_ipython
    assert get_ipython()
except:
    collect_ignore += [
        "src/importnb/compiler_ipython.py",
        "src/importnb/utils/ipython.py"
    ]

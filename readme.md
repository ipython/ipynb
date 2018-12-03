
__importnb__ imports notebooks as modules.  Notebooks are reusable as tests, source code, importable modules, and command line utilities.

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/deathbeds/importnb/master?urlpath=lab/tree/readme.ipynb)[![Documentation Status](https://readthedocs.org/projects/importnb/badge/?version=latest)](https://importnb.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/deathbeds/importnb.svg?branch=master)](https://travis-ci.org/deathbeds/importnb)[![PyPI version](https://badge.fury.io/py/importnb.svg)](https://badge.fury.io/py/importnb)![PyPI - Python Version](https://img.shields.io/pypi/pyversions/importnb.svg)![PyPI - Format](https://img.shields.io/pypi/format/importnb.svg)![PyPI - Format](https://img.shields.io/pypi/l/importnb.svg)[
![Conda](https://img.shields.io/conda/pn/conda-forge/importnb.svg)](https://anaconda.org/conda-forge/importnb)[
![GitHub tag](https://img.shields.io/github/tag/deathbeds/importnb.svg)](https://github.com/deathbeds/importnb/tree/master/src/importnb)

##### Installation

    pip install importnb
    
---

    conda install -c conda-forge importnb

---

# `importnb` for testing

After `importnb` is installed, [pytest](https://pytest.readthedocs.io/) will discover and import notebooks as tests.

    pytest index.ipynb

[`importnb`](https://github.com/deathbeds/importnb) imports notebooks as python modules, it does not compare outputs like [`nbval`](https://github.com/computationalmodelling/nbval).  These two `pytest` extensions complement each other well.

> Notebooks are often used as informal tests, now they can be formally tested with [pytest plugins](https://docs.pytest.org/en/latest/plugins.html)



---

# `importnb` for the commmand line

`importnb` can run notebooks as command line scripts.  Any literal variable in the notebook, may be applied as a parameter from the command line.

    ipython -m importnb -- index.ipynb --foo "A new value"

---

# `importnb` for Python and IPython


It is suggested to execute `importnb-install` to make sure that notebooks for each IPython session.

> Restart and run all or it didn't happen.

`importnb` excels in an interactive environment and if a notebook will __Restart and Run All__ then it may reused as python code. The `Notebook` context manager will allow notebooks _with valid names_ to import with Python.

    >>> from importnb import Notebook

### For brevity


```python
    with __import__('importnb').Notebook(): 
        import readme
```

> [`importnb.loader`](src/notebooks/loader.ipynb) will find notebooks available anywhere along the [`sys.path`](https://docs.python.org/2/library/sys.html#sys.path).

#### or explicity 


```python
    from importnb import Notebook
    with Notebook(): 
        import readme
```


```python
    foo = 42
    import readme
    assert readme.foo is 42
    assert readme.__file__.endswith('.ipynb')
```

[`importnb` readme](readme.ipynb)

### Modules may be reloaded 

The context manager is required to `reload` a module.


```python
    from importlib import reload
    with Notebook(): __name__ == '__main__' and reload(readme)
```

### Lazy imports

The `lazy` option will delay the evaluation of a module until one of its attributes are accessed the first time.


```python
    with Notebook(lazy=True):
        import readme
```


    Traceback (most recent call last):
    

      File "C:\Anaconda3\lib\site-packages\IPython\core\interactiveshell.py", line 3265, in run_code
        exec(code_obj, self.user_global_ns, self.user_ns)
    

      File "<ipython-input-6-a80fb0c23008>", line 2, in <module>
        import readme
    

      File "<frozen importlib._bootstrap>", line 971, in _find_and_load
    

      File "<frozen importlib._bootstrap>", line 955, in _find_and_load_unlocked
    

      File "<frozen importlib._bootstrap>", line 665, in _load_unlocked
    

      File "c:\users\deathbeds\pidgin\pidgin\loader.ipynb", line 71, in exec_module
        super().exec_module(module)
    

      File "<frozen importlib._bootstrap_external>", line 674, in exec_module
    

      File "<frozen importlib._bootstrap_external>", line 781, in get_code
    

      File "c:\users\deathbeds\importnb\src\importnb\loader.py", line 290, in source_to_code
        nodes = ast.parse(nodes)
    

      File "C:\Anaconda3\lib\ast.py", line 35, in parse
        return compile(source, filename, mode, PyCF_ONLY_AST)
    

      File "<unknown>", line 2
        """__importnb__ imports notebooks as modules.  Notebooks are reusable as tests, source code, importable modules, and command line utilities.
        ^
    IndentationError: unexpected indent
    


### Fuzzy File Names


```python
    if __name__ == '__main__':
        with Notebook():
            import __a_me
            
        assert __a_me.__file__ == readme.__file__
```


    Traceback (most recent call last):
    

      File "C:\Anaconda3\lib\site-packages\IPython\core\interactiveshell.py", line 3265, in run_code
        exec(code_obj, self.user_global_ns, self.user_ns)
    

      File "<ipython-input-7-15cace34bba8>", line 3, in <module>
        import __a_me
    

      File "<frozen importlib._bootstrap>", line 971, in _find_and_load
    

      File "<frozen importlib._bootstrap>", line 955, in _find_and_load_unlocked
    

      File "<frozen importlib._bootstrap>", line 665, in _load_unlocked
    

      File "c:\users\deathbeds\pidgin\pidgin\loader.ipynb", line 71, in exec_module
        super().exec_module(module)
    

      File "<frozen importlib._bootstrap_external>", line 674, in exec_module
    

      File "<frozen importlib._bootstrap_external>", line 781, in get_code
    

      File "c:\users\deathbeds\importnb\src\importnb\loader.py", line 290, in source_to_code
        nodes = ast.parse(nodes)
    

      File "C:\Anaconda3\lib\ast.py", line 35, in parse
        return compile(source, filename, mode, PyCF_ONLY_AST)
    

      File "<unknown>", line 2
        """__importnb__ imports notebooks as modules.  Notebooks are reusable as tests, source code, importable modules, and command line utilities.
        ^
    IndentationError: unexpected indent
    


Python does not provide a way to import file names starting with numbers of contains special characters.  `importnb` installs a fuzzy import logic to import files containing these edge cases.

    import __2018__6_01_A_Blog_Post
    
will find the first file matching `*2018*6?01?A?Blog?Post`.  Importing `Untitled314519.ipynb` could be supported with the query below.

    import __314519

### Docstring

The first markdown cell will become the module docstring.


```python
    if __name__ == '__main__':
        print(readme.__doc__.splitlines()[0])
```


    ---------------------------------------------------------------------------

    NameError                                 Traceback (most recent call last)

    <ipython-input-8-1bd926f9e7a3> in <module>
          1 if __name__ == '__main__':
    ----> 2     print(readme.__doc__.splitlines()[0])
    

    NameError: name 'readme' is not defined


Meaning non-code blocks can be executeb by [doctest]().


```python
    if __name__ == '__main__':
        __import__('doctest').testmod(readme)
```

# Import notebooks from files

Notebook names may not be valid Python paths.  In this case, use `Notebook.from_filename`.

       Notebook.from_filename('index.ipynb')
       
Import under the `__main__` context.
       
       Notebook('__main__').from_filename('index.ipynb')

# Parameterize Notebooks

Literal ast statements are converted to notebooks parameters.

In `readme`, `foo` is a parameter because it may be evaluated with ast.literal_val


```python
    if __name__ == '__main__':
        from importnb import Parameterize
        f = Parameterize.load(readme.__file__)
```

The parameterized module is a callable that evaluates with different literal statements.


```python
    if __name__ == '__main__': 
        assert callable(f)
        f.__signature__
```

    assert f().foo == 42
    assert f(foo='importnb').foo == 'importnb'

# Run Notebooks from the command line

Run any notebook from the command line with importnb.  Any parameterized expressions are available as parameters on the command line.

    

    !ipython -m importnb -- index.ipynb --foo "The new value"

## Integrations


### IPython

#### [IPython Extension](src/notebooks/loader.ipynb#IPython-Extensions)

Avoid the use of the context manager using loading importnb as IPython extension.

    %load_ext importnb
    
`%unload_ext importnb` will unload the extension.

#### Default Extension

`importnb` may allow notebooks to import by default with 

    !importnb-install
    

> If you'd like to play with source code on binder then you must execute the command above.  Toggle the markdown cell to a code cell and run it.

This extension will install a script into the default IPython profile startup that is called each time an IPython session is created.  

Uninstall the extension with `importnb-install`.

##### Run a notebook as a module

When the default extension is loaded any notebook can be run from the command line. After the `importnb` extension is created notebooks can be execute from the command line.

    ipython -m readme
    
In the command line context, `__file__ == sys.arv[0] and __name__ == '__main__'` .
    
> See the [deploy step in the travis build](https://github.com/deathbeds/importnb/blob/docs/.travis.yml#L19).

##### Parameterizable IPython commands

Installing the IPython extension allows notebooks to be computed from the command.  The notebooks are parameterizable from the command line.

    ipython -m readme -- --help

### py.test

`importnb` installs a pytest plugin when it is setup.  Any notebook obeying the py.test discovery conventions can be used in to pytest.  _This is great because notebooks are generally your first test._

    !ipython -m pytest -- src 
    
Will find all the test notebooks and configurations as pytest would any Python file.

### Setup

To package notebooks add `recursive-include package_name *.ipynb`

## Developer

* [Source Notebooks](src/notebooks/)
* [Transpiled Python Source](src/importnb/)
* [Tests](src/importnb/tests)

### Format and test the Source Code


```python
    if __name__ == '__main__':
        if globals().get('__file__', None) == __import__('sys').argv[0]:
            print(foo, __import__('sys').argv)
        else:
            from subprocess import call
            !ipython -m pytest
            """Formatting"""
            from pathlib import Path
            from importnb.utils.export import export
            root = 'src/importnb/notebooks/'
            for path in Path(root).rglob("""*.ipynb"""):                
                if 'checkpoint' not in str(path):
                    export(path, Path('src/importnb') / path.with_suffix('.py').relative_to(root))
            !jupyter nbconvert --to markdown --stdout index.ipynb > readme.md
            
```


```python
    if __name__ == '__main__':
        try:
            from IPython.display import display, Image
            from IPython.utils.capture import capture_output
            from IPython import get_ipython
            with capture_output(): 
                get_ipython().system("cd docs && pyreverse importnb -opng -pimportnb")
            display(Image(url='docs/classes_importnb.png', ))
        except: ...
```

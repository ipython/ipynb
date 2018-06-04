
__importnb__ imports notebooks as modules & packages.

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/deathbeds/importnb/master?urlpath=lab/tree/readme.ipynb)[![Build Status](https://travis-ci.org/deathbeds/importnb.svg?branch=master)](https://travis-ci.org/deathbeds/importnb)[![PyPI version](https://badge.fury.io/py/importnb.svg)](https://badge.fury.io/py/importnb)![PyPI - Python Version](https://img.shields.io/pypi/pyversions/importnb.svg)![PyPI - Format](https://img.shields.io/pypi/format/importnb.svg)![PyPI - Format](https://img.shields.io/pypi/l/importnb.svg)[
![Conda](https://img.shields.io/conda/pn/conda-forge/importnb.svg)](https://anaconda.org/conda-forge/importnb)[
![GitHub tag](https://img.shields.io/github/tag/deathbeds/importnb.svg)](https://github.com/deathbeds/importnb/tree/master/src/importnb)

    pip install importnb
    
---

    conda install -c conda-forge importnb

# `importnb` works in Python and IPython

Use the `Notebook` context manager.

    >>> from importnb import Notebook

### For brevity

[`importnb.loader`](src/notebooks/loader.ipynb) will find notebooks available anywhere along the [`sys.path`](https://docs.python.org/2/library/sys.html#sys.path).


```python
    with __import__('importnb').Notebook(): 
        import readme
```

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

### Modules may be reloaded 

The context manager is required to `reload` a module.


```python
    from importlib import reload
    with Notebook():
        reload(readme)
```

### Partial loading

The [`importnb.loader.Notebook`](src/notebooks/loader.ipynb#Partial-Loader) will __import__ a notebook even if there is an exception by supplying the `exceptions` option.  The __exception__ is found on `module._exception`.


```python
    with Notebook(exceptions=BaseException):
        try: from . import readme
        except: import readme
```

### Lazy imports

The `lazy` option will delay the evaluation of a module until one of its attributes are accessed the first time.


```python
    with Notebook(lazy=True):
        import readme
```

## Capture Outputs

`importnb` can capture the `stdout`, `stderr`, and `display` in the context manager.  The arguments are similar to `IPython.util.capture.capture_output`.


```python
    with Notebook(stdout=True, stderr=True, display=True) as output:
        import readme
```

### Docstring

The first markdown cell will become the module docstring.


```python
    if __name__ == '__main__':
        print(readme.__doc__.splitlines()[0])
```

    __importnb__ imports notebooks as modules & packages.


Meaning non-code blocks can be executeb by [doctest]().


```python
    if __name__ == '__main__':
        __import__('doctest').testmod(readme)
```

# Import notebooks from files

Notebook names may not be valid Python paths.  In this case, use `Notebook.from_filename`.

       Notebook.from_filename('readme.ipynb')
       
Import under the `__main__` context.
       
       Notebook.from_filename('readme.ipynb', main=True)

# Parameterize Notebooks

Literal ast statements are converted to notebooks parameters.

In `readme`, `foo` is a parameter because it may be evaluated with ast.literal_val


```python
    from importnb import Parameterize
    f = Parameterize().from_filename(readme.__file__)
    
```

The parameterized module is a callable that evaluates with different literal statements.


```python
    assert callable(f)
    f.__signature__
```




    <Signature (*, foo=42)>



    assert f().foo == 42
    assert f(foo='importnb').foo == 'importnb'

# Run Notebooks from the command line

Run any notebook from the command line with importnb.  Any parameterized expressions are available as parameters on the command line.

    !ipython -m importnb -- readme.ipynb --foo "I'm the new foo"
    !python -m importnb readme.ipynb --foo "No I am!"
    
After installing the IPython Extension any notebook may be run as any a command line script

    !ipython -m readme -- --foo "look at me"


## Integrations


### IPython

#### [IPython Extension](src/notebooks/loader.ipynb#IPython-Extensions)

Avoid the use of the context manager using loading importnb as IPython extension.

    %load_ext importnb
    
`%unload_ext importnb` will unload the extension.

#### Default Extension

`importnb` may allow notebooks to import by default with 

    importnb-install
    
This extension will install a script into the default IPython profile startup that is called each time an IPython session is created.  

Uninstall the extension with `importnb-install`.

##### Run a notebook as a module

When the default extension is loaded any notebook can be run from the command line. After the `importnb` extension is created notebooks can be execute from the command line.

    ipython -m readme
    
In the command line context, `__file__ == sys.arv[0] and __name__ == '__main__'` .
    
> See the [deploy step in the travis build](https://github.com/deathbeds/importnb/blob/docs/.travis.yml#L19).

### py.test

`importnb` installs a pytest plugin when it is setup.  Any notebook obeying the py.test discovery conventions can be used in to pytest.  _This is great because notebooks are generally your first test._

    !ipython -m pytest -- src 
    
Will find all the test notebooks and configurations as pytest would any Python file.

### Setup

To package notebooks add `recursive-include package_name *.ipynb`

### [Watchdog](https://github.com/gorakhargosh/watchdog/tree/master/src/watchdog/tricks) _Experimental_

    pip install importnb[watch]

`importnb` exports a watchdog trick to watch files and apply command like operations on their module path.

#### Tricks File

For example, create a file called `tricks.yaml` containing

    tricks:
    - importnb.utils.watch.ModuleTrick:
          patterns: ['*.ipynb']
          shell_command: ipython -m ${watch_dest_path}
      
#### Run the watcher in a terminal

    watchmedo tricks tricks.yaml
      
> [`tricks.yaml`](tricks.yaml) is a concrete implementation of `tricks.yaml`

## Developer

* [Source Notebooks](src/notebooks/)
* [Transpiled Python Source](src/importnb/)
* [Tests](src/importnb/tests)

### Format and test the Source Code


```python
    if __name__ == '__main__':
        try:
            from subprocess import call
            from importnb.capture import capture_output
            with capture_output() as out: 
                call("ipython -m pytest -- src ".split())
            print('plugins'+out.stdout.split('plugins', 1)[-1])
        except:
            ...
            print(foo)
            
        if 'kernel' in __import__('sys').argv[0]:
            """Formatting"""
            from pathlib import Path
            from importnb.utils.export import export
            root = 'src/importnb/notebooks/'
            for path in Path(root).rglob("""*.ipynb"""):                
                if 'checkpoint' not in str(path):
                    export(path, Path('src/importnb') / path.with_suffix('.py').relative_to(root))
            call("jupyter nbconvert --to markdown readme.ipynb".split())
                    
        

```

    if __name__ == '__main__':
        from IPython.display import display, Image
        !pyreverse importnb -opng -pimportnb
        display(*map(Image, ('classes_importnb.png', 'packages_importnb.png')))

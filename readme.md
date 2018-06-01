
__importnb__ imports notebooks as modules & packages.

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/deathbeds/importnb/master?urlpath=lab/tree/readme.ipynb)[![Build Status](https://travis-ci.org/deathbeds/importnb.svg?branch=master)](https://travis-ci.org/deathbeds/importnb)[![PyPI version](https://badge.fury.io/py/importnb.svg)](https://badge.fury.io/py/importnb)![PyPI - Python Version](https://img.shields.io/pypi/pyversions/importnb.svg)![PyPI - Format](https://img.shields.io/pypi/format/importnb.svg)![PyPI - Format](https://img.shields.io/pypi/l/importnb.svg)[
![Conda](https://img.shields.io/conda/pn/conda-forge/importnb.svg)](https://anaconda.org/conda-forge/importnb)[
![GitHub tag](https://img.shields.io/github/tag/deathbeds/importnb.svg)](https://github.com/deathbeds/importnb/tree/master/src/importnb)



    pip install importnb
    
---

    conda install -c conda-forge importnb

# `importnb` works in Python and IPython

Use the `Notebook` context manager.

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

The [`importnb.loader.Partial`](src/notebooks/loader.ipynb#Partial-Loader) will __import__ a notebook even if there is an exception.  The __exception__ is found on `module.__exception`.


```python
    with Notebook(exceptions=BaseException):
        try: from . import readme
        except: import readme
```

### Lazy imports

The [`importnb.loader.Lazy`](src/notebooks/loader.ipynb#Lazy-Loader) will delay the evaluation of a module until one of its attributes are accessed the first time.


```python
    with Notebook(lazy=True):
        import readme
```

## Capture Outputs

`importnb` can capture the `stdout`, `stderr`, and `display` in the context manager.


```python
    with Notebook(stdout=True, stderr=True, display=True) as output:
        import readme
```

### Docstring

The first cell is the module docstring.


```python
    if __name__ == '__main__':
        print(readme.__doc__.splitlines()[0])
```

    __importnb__ imports notebooks as modules & packages.


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
    
> See the [deploy step in the travis build](https://github.com/deathbeds/importnb/blob/docs/.travis.yml#L19).

### py.test

`importnb` installs a pytest plugin when it is setup.  Any notebook obeying the py.test discovery conventions can be used in to pytest.  _This is great because notebooks are generally your first test._

### Setup

To package notebooks add `recursive-include package_name *.ipynb`

### [Watchdog](https://github.com/gorakhargosh/watchdog/tree/master/src/watchdog/tricks)

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
    from IPython import get_ipython
```


```python
    if __name__ == '__main__':
        from pathlib import Path
        from importnb.utils.export import export
        from importnb.capture import capture_output
        root = 'src/importnb/notebooks/'
        for path in Path(root).rglob("""*.ipynb"""):                
            if 'checkpoint' not in str(path):
                export(path, Path('src/importnb') / path.with_suffix('.py').relative_to(root))
        with capture_output() as out:
            !ipython -m pytest -- src 
        print('plugins'+out.stdout.split('plugins', 1)[-1])
```

    plugins: ignore-flaky-0.1.1, forked-0.2, cov-2.5.1, benchmark-3.1.1, importnb-0.3.0
    collected 24 items                                                             [0m
    
    src/importnb/tests/test_importnb.ipynb::test_single_file_with_context [32mPASSED[0m[36m [  4%][0m
    src/importnb/tests/test_importnb.ipynb::test_from_filename [32mPASSED[0m[36m        [  8%][0m
    src/importnb/tests/test_importnb.ipynb::test_from_execute [32mPASSED[0m[36m         [ 12%][0m
    src/importnb/tests/test_importnb.ipynb::test_with_doctest [32mPASSED[0m[36m         [ 16%][0m
    src/importnb/tests/test_importnb.ipynb::test_from_filename_main [32mPASSED[0m[36m   [ 20%][0m
    src/importnb/tests/test_importnb.ipynb::test_parameterize [32mPASSED[0m[36m         [ 25%][0m
    src/importnb/tests/test_importnb.ipynb::test_python_file [32mPASSED[0m[36m          [ 29%][0m
    src/importnb/tests/test_importnb.ipynb::test_single_file_with_capture [32mPASSED[0m[36m [ 33%][0m
    src/importnb/tests/test_importnb.ipynb::test_capturer [32mPASSED[0m[36m             [ 37%][0m
    src/importnb/tests/test_importnb.ipynb::test_single_file_with_lazy [32mPASSED[0m[36m [ 41%][0m
    src/importnb/tests/test_importnb.ipynb::test_single_file_without_context [33mXPASS[0m[36m [ 45%][0m
    src/importnb/tests/test_importnb.ipynb::test_single_file_relative 42
    [33mxfail[0m[36m  [ 50%][0m
    src/importnb/tests/test_importnb.ipynb::test_single_with_extension [32mPASSED[0m[36m [ 54%][0m
    src/importnb/tests/test_importnb.ipynb::test_package [32mPASSED[0m[36m              [ 58%][0m
    src/importnb/tests/test_importnb.ipynb::test_package_failure [33mxfail[0m[36m       [ 62%][0m
    src/importnb/tests/test_importnb.ipynb::test_package_failure_partial [32mPASSED[0m[36m [ 66%][0m
    src/importnb/tests/test_importnb.ipynb::test_tmp_dir [32mPASSED[0m[36m              [ 70%][0m
    src/importnb/tests/test_unittests.ipynb::TestPartial::test_exception [32mPASSED[0m[36m [ 75%][0m
    src/importnb/tests/test_unittests.ipynb::TestPartial::test_traceback [32mPASSED[0m[36m [ 79%][0m
    src/importnb/tests/test_unittests.ipynb::TestContext::test_import [32mPASSED[0m[36m [ 83%][0m
    src/importnb/tests/test_unittests.ipynb::TestContext::test_reload_with_context [32mPASSED[0m[36m [ 87%][0m
    src/importnb/tests/test_unittests.ipynb::TestRemote::test_imports [33mSKIPPED[0m[36m [ 91%][0m
    src/importnb/tests/test_unittests.ipynb::TestExtension::test_failure [33mxfail[0m[36m [ 95%][0m
    src/importnb/tests/test_unittests.ipynb::TestExtension::test_import [32mPASSED[0m[36m [100%][0m
    
    ---------- coverage: platform darwin, python 3.5.4-final-0 -----------
    Name                                    Stmts   Miss  Cover
    -----------------------------------------------------------
    src/importnb/__init__                      11     11     0%
    src/importnb/__main__                       3      3     0%
    src/importnb/_version                       1      1     0%
    src/importnb/capture                       59     59     0%
    src/importnb/decoder                       35     24    31%
    src/importnb/execute                       90     48    47%
    src/importnb/loader                       132     78    41%
    src/importnb/nbtest                        34     34     0%
    src/importnb/notebooks/__init__             0      0   100%
    src/importnb/notebooks/utils/__init__       0      0   100%
    src/importnb/nunittest                     44     44     0%
    src/importnb/parameterize                  81     44    46%
    src/importnb/path_hooks                    84     35    58%
    src/importnb/tests/failure                  1      0   100%
    src/importnb/tests/import_this              1      0   100%
    src/importnb/tests/pyimport                 3      0   100%
    src/importnb/tests/test_importnb            1      0   100%
    src/importnb/tests/test_unittests           1      0   100%
    src/importnb/usage/__init__                 0      0   100%
    src/importnb/utils/__init__                 0      0   100%
    src/importnb/utils/export                  33     33     0%
    src/importnb/utils/ipython                 41     41     0%
    src/importnb/utils/nbdoctest               36     36     0%
    src/importnb/utils/pytest_plugin           24     15    38%
    src/importnb/utils/setup                   52     52     0%
    src/importnb/utils/watch                   20     20     0%
    -----------------------------------------------------------
    TOTAL                                     787    578    27%
    
    
    [32m[1m========== 19 passed, 1 skipped, 3 xfailed, 1 xpassed in 3.98 seconds ==========[0m
    



```python
    if __name__ == '__main__':
        !jupyter nbconvert --to markdown readme.ipynb
```

    [NbConvertApp] Converting notebook readme.ipynb to markdown
    [NbConvertApp] Writing 11209 bytes to readme.md


    if __name__ == '__main__':
        from IPython.display import display, Image
        !pyreverse importnb -opng -pimportnb
        display(*map(Image, ('classes_importnb.png', 'packages_importnb.png')))

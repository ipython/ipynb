
__importnb__ imports notebooks as modules & packages.

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/deathbeds/importnb/master?urlpath=lab/tree/readme.ipynb)[![Build Status](https://travis-ci.org/deathbeds/importnb.svg?branch=master)](https://travis-ci.org/deathbeds/importnb)[![PyPI version](https://badge.fury.io/py/importnb.svg)](https://badge.fury.io/py/importnb)![PyPI - Python Version](https://img.shields.io/pypi/pyversions/importnb.svg)![PyPI - Format](https://img.shields.io/pypi/format/importnb.svg)![PyPI - Format](https://img.shields.io/pypi/l/importnb.svg)



    pip install importnb

# `importnb` works in Python and IPython

Use the `Notebook` context manager.

### For brevity


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

## Integrations


### IPython

#### Extension

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

### Setuptools

`importnb` provides a setuptool command that will place notebooks in a source distribution.  In setuptools, update the command classs with

    from importnb.utils.setup import build_ipynb
    setup(
        ...,
        cmdclass=dict(build_py=build_ipynb)
        ...,)

### [Watchdog](https://github.com/gorakhargosh/watchdog/tree/master/src/watchdog/tricks)

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

* [Tests](tests/test_importnb.ipynb)
* [Source Notebooks](src/notebooks/)
* [Transpiled Python Source](src/importnb/)

### Format and test the Source Code


```python
    if __name__ == '__main__':
        from pathlib import Path
        import black
        from importnb.compiler_python import ScriptExporter
        for path in Path('src/notebooks/').rglob("""*.ipynb"""):
            if 'checkpoint' not in str(path):
                print(path)
                (Path('src/importnb') / path.with_suffix('.py').relative_to('src/notebooks')).write_text(
                black.format_str(ScriptExporter().from_filename(path)[0], 100))
            
        __import__('unittest').main(module='src.importnb.tests.test_unittests', argv="discover --verbose".split(), exit=False) 

```

    src/notebooks/compiler_ipython.ipynb
    src/notebooks/compiler_python.ipynb
    src/notebooks/decoder.ipynb
    src/notebooks/exporter.ipynb
    src/notebooks/loader.ipynb
    src/notebooks/utils/__init__.ipynb
    src/notebooks/utils/ipython.ipynb
    src/notebooks/utils/pytest_plugin.ipynb
    src/notebooks/utils/setup.ipynb
    src/notebooks/utils/watch.ipynb


    test_import (src.importnb.tests.test_unittests.TestContext) ... ok
    test_reload_with_context (src.importnb.tests.test_unittests.TestContext) ... ok
    test_reload_without_context (src.importnb.tests.test_unittests.TestContext) ... skipped 'importnb is probably installed'
    test_failure (src.importnb.tests.test_unittests.TestExtension) ... unexpected success
    test_import (src.importnb.tests.test_unittests.TestExtension) ... ok
    test_exception (src.importnb.tests.test_unittests.TestPartial) ... ok
    test_traceback (src.importnb.tests.test_unittests.TestPartial) ... ok
    test_imports (src.importnb.tests.test_unittests.TestRemote) ... skipped 'requires IP'
    
    ----------------------------------------------------------------------
    Ran 8 tests in 1.014s
    
    FAILED (skipped=2, unexpected successes=1)


### Format the Github markdown files


```python
    if __name__ == '__main__':
        from nbconvert.exporters.markdown import MarkdownExporter
        for path in map(Path, ('readme.ipynb', 'changelog.ipynb')):
            path.with_suffix('.md').write_text(MarkdownExporter().from_filename(path)[0])
```

### Format the Github Pages documentation

We use `/docs` as the `local_dir`.


```python
    if __name__ == '__main__':
        from nbconvert.exporters.markdown import MarkdownExporter
        files = 'readme.ipynb', 'changelog.ipynb'
        for doc in map(Path, files):
            to = ('docs' / doc.with_suffix('.md'))
            to.parent.mkdir(exist_ok=True)
            to.write_text(MarkdownExporter().from_filename(doc)[0])
```


__importnb__ supports the ability to use Jupyter notebooks as python source.

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/deathbeds/importnb/master?urlpath=lab/tree/readme.ipynb)[![Build Status](https://travis-ci.org/deathbeds/importnb.svg?branch=master)](https://travis-ci.org/deathbeds/importnb)

    pip install importnb

## Jupyter Extension

    %load_ext importnb    


```python
    foo = 42
    import readme
    assert readme.foo is 42
    assert readme.__file__.endswith('.ipynb')
```

Notebooks maybe reloaded with the standard Python Import machinery.


```python
    from importnb import Notebook, reload
    reload(readme);
```

## Unload the extension

    %unload_ext importnb

## Context Manager


```python
    with Notebook(): 
        import readme
        reload(readme)
```

## Integrations

`importnb` integrates with IPython, py.test, and setuptools.


### IPython

`importnb` may allow notebooks to import by default with 

    %load_ext importnb.utils.ipython
    
This extension will install a script into the default IPython profile startup that is called each time an IPython session is created.  

#### Command

After the `importnb` extension is created notebooks can be execute from the command line.

    ipython -m readme

### Unloading the Extension

The default settings may be discarded temporarily with

    %unload_ext importnb
    

### py.test

`importnb` installs a pytest plugin when it is setup.  Any notebook obeying the py.test discovery conventions can be used in to pytest.  _This is great because notebooks are generally your first test._

### Setuptools

`importnb` provides a setuptool command that will place notebooks in a source distribution.  In setuptools, update the command classs with

    from importnb.utils.setup import build_ipynb
    setup(
        ...,
        cmdclass=dict(build_py=build_ipynb)
        ...,)

## Developer


```python
    if __name__ == '__main__':
        from pathlib import Path
        import black
        from nbconvert.exporters.markdown import MarkdownExporter
        from importnb.compiler_python import ScriptExporter
        for path in Path('src/notebooks/').rglob("""*.ipynb"""):
            
            'checkpoint' not in str(path) and (Path('src/importnb') / path.with_suffix('.py').relative_to('src/notebooks')).write_text(
                black.format_str(ScriptExporter().from_filename(path)[0], 100))
        for path in map(Path, ('readme.ipynb', 'changelog.ipynb')):
            path.with_suffix('.md').write_text(MarkdownExporter().from_filename(path)[0])

        __import__('unittest').main(module='tests', argv="discover --verbose".split(), exit=False)

```

    test_import (tests.test_.TestContext) ... ok
    test_reload_with_context (tests.test_.TestContext) ... ok
    test_reload_without_context (tests.test_.TestContext) ... skipped 'importnb is probably installed'
    test_failure (tests.test_.TestExtension) ... expected failure
    test_import (tests.test_.TestExtension) ... ok
    test_exception (tests.test_.TestPartial) ... ok
    test_traceback (tests.test_.TestPartial) ... ok
    test_imports (tests.test_.TestRemote) ... skipped 'requires IP'
    
    ----------------------------------------------------------------------
    Ran 8 tests in 2.021s
    
    OK (skipped=2, expected failures=1)


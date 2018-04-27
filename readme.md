
__importnb__ supports the ability to use Jupyter notebooks as python source.

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/deathbeds/importnb/master?urlpath=lab/tree/readme.ipynb)[![Build Status](https://travis-ci.org/deathbeds/importnb.svg?branch=master)](https://travis-ci.org/deathbeds/importnb)

    pip install importnb

## Jupyter Extension


```python
    %reload_ext importnb
    foo = 42
    import readme
    assert readme.foo is 42
    assert readme.__file__.endswith('.ipynb')
```

Notebooks maybe reloaded with the standard Python Import machinery.


```python
    from importnb import Notebook, reload
    
    if __name__ == '__main__':
        %reload_ext importnb
        reload(readme)
        %unload_ext importnb
```

## Context Manager


```python
    try:  
        reload(readme)
    except: ...
    with Notebook(): 
        reload(readme)
```

## Developer


```python
    if __name__ == '__main__':
        from pathlib import Path
        import black
        from nbconvert.exporters.markdown import MarkdownExporter
        from importnb.compiler_python import ScriptExporter
        for path in Path('importnb').glob('*.ipynb'):
            path.with_suffix('.py').write_text(
                black.format_str(ScriptExporter().from_filename(path)[0], 100))
        for path in map(Path, ('readme.ipynb', 'changelog.ipynb')):
            path.with_suffix('.md').write_text(MarkdownExporter().from_filename(path)[0])
        __import__('unittest').main(module='tests', argv="discover".split(), exit=False)
```

    ..xx....
    ----------------------------------------------------------------------
    Ran 8 tests in 2.085s
    
    OK (expected failures=2)


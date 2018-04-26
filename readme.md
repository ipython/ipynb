
__importnb__ supports the ability to use Jupyter notebooks as python source.

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/deathbeds/importnb/master?filepath=readme.ipynb)[![Build Status](https://travis-ci.org/deathbeds/importnb.svg?branch=master)](https://travis-ci.org/deathbeds/importnb)

    pip install importnb

## Jupyter Extension


```python
    if __name__ == '__main__':
        %reload_ext importnb
        import readme
        assert readme.foo is 42
        assert readme.__file__.endswith('.ipynb')
    else: 
        foo = 42
        
```

Notebooks maybe reloaded with the standard Python Import machinery.


```python
    if __name__ == '__main__':
        from importnb import Notebook, reload
        reload(readme)
        %unload_ext importnb
```

## Context Manager


```python
    if __name__ == '__main__':
        try:  
            reload(readme)
            assert None, """Reloading should not work when the extension is unloaded"""
        except AttributeError: 
            with Notebook(): reload(readme)
```

## Developer


```python
    if __name__ == '__main__':
        from pathlib import Path
        import black, subprocess, warnings
        from nbconvert.exporters.markdown import MarkdownExporter
        from importnb.compiler_python import ScriptExporter
        for path in Path('importnb').glob('*.ipynb'):
            path.with_suffix('.py').write_text(
                black.format_str(ScriptExporter().from_filename(str(path))[0], 100))
        Path('readme.md').write_text(MarkdownExporter().from_filename('readme.ipynb')[0])
        __import__('unittest').main(module='tests', argv="discover".split(), exit=False)
```

    ..xx....
    ----------------------------------------------------------------------
    Ran 8 tests in 2.087s
    
    OK (expected failures=2)


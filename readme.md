
__importnb__ supports the ability to use Jupyter notebooks as python source.

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/deathbeds/importnb/master?urlpath=lab/tree/readme.ipynb)[![Build Status](https://travis-ci.org/deathbeds/importnb.svg?branch=master)](https://travis-ci.org/deathbeds/importnb)

    pip install importnb

## Jupyter Extension


```python
    %reload_ext importnb
```


```python
    foo = 42
    
    import readme
    assert readme.foo is 42
    assert readme.__file__.endswith('.ipynb')
        
        
```


    ---------------------------------------------------------------------------

    AttributeError                            Traceback (most recent call last)

    <ipython-input-1-8be062be31f2> in <module>()
          1 get_ipython().run_line_magic('reload_ext', 'importnb')
    ----> 2 import readme
          3 assert readme.foo is 42
          4 assert readme.__file__.endswith('.ipynb')
          5 if __name__ != '__main__':


    ~/anaconda/envs/p6/lib/python3.6/importlib/_bootstrap.py in _find_and_load(name, import_)


    ~/anaconda/envs/p6/lib/python3.6/importlib/_bootstrap.py in _find_and_load_unlocked(name, import_)


    ~/anaconda/envs/p6/lib/python3.6/importlib/_bootstrap.py in _load_unlocked(spec)


    ~/importnb/importnb/loader.py in exec_module(Loader, module)
         68         module.__output__ = None
         69         if get_ipython and Loader.capture:
    ---> 70             return Loader.exec_module_capture(module)
         71         else:
         72             return super().exec_module(module)


    ~/importnb/importnb/loader.py in exec_module_capture(Loader, module)
         77         with capture_output(stdout=False, stderr=False) as output:
         78             try:
    ---> 79                 super().exec_module(module)
         80             except type("pass", (BaseException,), {}):
         81                 ...


    ~/importnb/readme.ipynb in <module>()
         36     "    %reload_ext importnb\n",
         37     "    import readme\n",
    ---> 38     "    assert readme.foo is 42\n",
         39     "    assert readme.__file__.endswith('.ipynb')\n",
         40     "    if __name__ != '__main__':\n",


    AttributeError: module 'readme' has no attribute 'foo'


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

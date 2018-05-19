
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

    [NbConvertApp] Converting notebook readme.ipynb to markdown
    [NbConvertApp] Writing 10372 bytes to readme.md
    [NbConvertApp] Converting notebook readme.ipynb to markdown
    [NbConvertApp] Writing 10372 bytes to readme.md


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

    [NbConvertApp] Converting notebook readme.ipynb to markdown
    [NbConvertApp] Writing 10372 bytes to readme.md


### Partial loading

The [`importnb.loader.Partial`](src/notebooks/loader.ipynb#Partial-Loader) will __import__ a notebook even if there is an exception.  The __exception__ is found on `module.__exception`.


```python
    from importnb import Partial
    with Partial():
        import readme
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
    f = Parameterize(readme)
    
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
    if __name__ == '__main__':
        from pathlib import Path
        from nbconvert.exporters.python import PythonExporter
        from importnb.compile import export
        for path in Path('src/notebooks/').rglob("""*.ipynb"""):                
            if 'checkpoint' not in str(path):
                export(path, Path('src/importnb') / path.with_suffix('.py').relative_to('src/notebooks'))
            
        __import__('unittest').main(module='src.importnb.tests.test_unittests', argv="discover --verbose".split(), exit=False) 

```


    ---------------------------------------------------------------------------

    TemplateNotFound                          Traceback (most recent call last)

    <ipython-input-10-04e274158377> in <module>()
          5     for path in Path('src/notebooks/').rglob("""*.ipynb"""):
          6         if 'checkpoint' not in str(path):
    ----> 7             export(path, Path('src/importnb') / path.with_suffix('.py').relative_to('src/notebooks'))
          8 
          9     __import__('unittest').main(module='src.importnb.tests.test_unittests', argv="discover --verbose".split(), exit=False)


    ~/importnb/src/importnb/compile.py in export(file, to)
         59 
         60     exporter = ImportNbStyleExporter()
    ---> 61     code = exporter.from_filename(file)[0]
         62     if to:
         63         Path(to).with_suffix(exporter.file_extension).write_text(code)


    ~/anaconda/envs/p6/lib/python3.6/site-packages/nbconvert/exporters/exporter.py in from_filename(self, filename, resources, **kw)
        172 
        173         with io.open(filename, encoding='utf-8') as f:
    --> 174             return self.from_file(f, resources=resources, **kw)
        175 
        176 


    ~/anaconda/envs/p6/lib/python3.6/site-packages/nbconvert/exporters/exporter.py in from_file(self, file_stream, resources, **kw)
        190 
        191         """
    --> 192         return self.from_notebook_node(nbformat.read(file_stream, as_version=4), resources=resources, **kw)
        193 
        194 


    ~/importnb/src/importnb/compile.py in from_notebook_node(self, nb, resources, **kw)
         47 
         48     def from_notebook_node(self, nb, resources=None, **kw):
    ---> 49         code, resources = super().from_notebook_node(nb, resources=resources, **kw)
         50         try:
         51             from black import format_str


    ~/anaconda/envs/p6/lib/python3.6/site-packages/nbconvert/exporters/templateexporter.py in from_notebook_node(self, nb, resources, **kw)
        293 
        294         # Top level variables are passed to the template_exporter here.
    --> 295         output = self.template.render(nb=nb_copy, resources=resources)
        296         return output, resources
        297 


    ~/anaconda/envs/p6/lib/python3.6/site-packages/nbconvert/exporters/templateexporter.py in template(self)
        109     def template(self):
        110         if self._template_cached is None:
    --> 111             self._template_cached = self._load_template()
        112         return self._template_cached
        113 


    ~/anaconda/envs/p6/lib/python3.6/site-packages/nbconvert/exporters/templateexporter.py in _load_template(self)
        264         self.log.debug("Attempting to load template %s", template_file)
        265         self.log.debug("    template_path: %s", os.pathsep.join(self.template_path))
    --> 266         return self.environment.get_template(template_file)
        267 
        268     def from_notebook_node(self, nb, resources=None, **kw):


    ~/anaconda/envs/p6/lib/python3.6/site-packages/jinja2/environment.py in get_template(self, name, parent, globals)
        828         if parent is not None:
        829             name = self.join_path(name, parent)
    --> 830         return self._load_template(name, self.make_globals(globals))
        831 
        832     @internalcode


    ~/anaconda/envs/p6/lib/python3.6/site-packages/jinja2/environment.py in _load_template(self, name, globals)
        802                                          template.is_up_to_date):
        803                 return template
    --> 804         template = self.loader.load(self, name, globals)
        805         if self.cache is not None:
        806             self.cache[cache_key] = template


    ~/anaconda/envs/p6/lib/python3.6/site-packages/jinja2/loaders.py in load(self, environment, name, globals)
        406             except TemplateNotFound:
        407                 pass
    --> 408         raise TemplateNotFound(name)
        409 
        410     def list_templates(self):


    TemplateNotFound: /Users/tonyfast/importnb/src/importnb/block_string.tpl



```python
    !jupyter nbconvert --to markdown readme.ipynb
```

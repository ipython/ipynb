
# coding: utf-8

# # by *convention* Notebooks __import__
# 
# __rites.rites__ makes all notebooks __import__able as Python source.

# In[1]:


try:
    from .compiler import Compile, AST
except:
    from compiler import Compile, AST


# # The [Import Loader](https://docs.python.org/3/reference/import.html#loaders)
# 
# `rites` uses as much of the Python import system as it can.

# In[2]:


from importlib.machinery import SourceFileLoader


# In[3]:


class Notebook(SourceFileLoader):
    """A SourceFileLoader for notebooks that provides line number debugginer in the JSON source."""
    EXTENSION_SUFFIXES = '.ipynb',
    def exec_module(Loader, module):
        from IPython.utils.capture import capture_output    
        with capture_output(stdout=False, stderr=False) as output: 
            try: 
                super().exec_module(module)
            except type('pass', (BaseException,), {}): ...
            finally: module.__output__ = output
        return module

    def source_to_code(Notebook, data, path):
        with __import__('io').BytesIO(data) as stream:
            return Compile().from_file(stream, filename=Notebook.path, name=Notebook.name)


# ## Path Hook
# 
# Create a [path_hook](https://docs.python.org/3/reference/import.html#import-hooks) rather than a `meta_path` so any module containing notebooks is accessible.

# In[4]:


import sys


# In[5]:


_NATIVE_HOOK = sys.path_hooks
def update_hooks(loader=None):
    """Update the sys.meta_paths with the PartialLoader.
    
    """
    global _NATIVE_HOOK
    from importlib.machinery import FileFinder
    if loader:
        for i, hook in enumerate(sys.path_hooks):
            closure = getattr(hook, '__closure__', None)
            if closure and closure[0].cell_contents is FileFinder:
                sys.path_hooks[i] = FileFinder.path_hook(
                    (loader, list(loader.EXTENSION_SUFFIXES)), *closure[1].cell_contents)
    else: sys.path_hooks = _NATIVE_HOOK
    sys.path_importer_cache.clear()


# # IPython Extensions

# In[6]:


def load_ipython_extension(ip=None): update_hooks(Notebook)
def unload_ipython_extension(ip=None): update_hooks()


# ### Force the docstring for rites itself.

# In[ ]:


class Test(__import__('unittest').TestCase): 
    def setUp(Test):
        from nbformat import write, v4
        load_ipython_extension()
        with open('test_loader.ipynb', 'w') as file:
            write(v4.new_notebook(cells=[
                v4.new_code_cell("test = 42")
            ]), file)
            
    def runTest(Test):
        import test_loader
        assert test_loader.__file__.endswith('.ipynb')
        assert test_loader.test is 42
        assert isinstance(test_loader, __import__('types').ModuleType)
        
    def tearDown(Test):
        get_ipython().run_line_magic('rm', 'test_loader.ipynb')
        unload_ipython_extension()


# # Developer

# In[ ]:


if __name__ ==  '__main__':
#         __import__('doctest').testmod(verbose=2)
    __import__('unittest').TextTestRunner().run(Test())
    get_ipython().system('jupyter nbconvert --to script __init__.ipynb')


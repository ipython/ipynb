
# coding: utf-8

# # The [Import Loader](https://docs.python.org/3/reference/import.html#loaders)
# 
# `rites` uses as much of the Python import system as it can.

# In[1]:


try:
    from .compiler import Compile, AST
except:
    from compiler import Compile, AST
import inspect, sys, warnings
from importlib.machinery import SourceFileLoader
from importlib._bootstrap_external import FileFinder
from traceback import print_exc


# In[2]:


def update_path_hooks(id, *loaders):
    sys.path_hooks.pop(id)
    sys.path_hooks.insert(id, (FileFinder.path_hook(*tuple(loaders))))


# In[3]:


class ContextManager:
    def __enter__(self):
        for i, hook in enumerate(sys.path_hooks):
            cls = type(self)
            try:
                closure = inspect.getclosurevars(hook).nonlocals
                if issubclass(closure['cls'], FileFinder):
                    update_path_hooks(i, (cls, (list(self.EXTENSION_SUFFIXES))), *(
                        (cls, ext) for cls, ext in closure['loader_details'] if not issubclass(cls, Notebook)))
            except TypeError: ...
        sys.path_importer_cache.clear()
                
                
    def __exit__(self, exception_type=None, exception_value=None, traceback=None):
        for i, hook in enumerate(sys.path_hooks):
            try:
                closure = inspect.getclosurevars(hook).nonlocals
                if issubclass(closure['cls'], FileFinder):
                    update_path_hooks(i, *(
                        (cls, ext) for cls, ext in closure['loader_details'] if not issubclass(cls, type(self))
                    ))
            except TypeError: ...
        sys.path_importer_cache.clear()
        


# In[5]:


class Notebook(SourceFileLoader, ContextManager):
    """A SourceFileLoader for notebooks that provides line number debugginer in the JSON source."""
    EXTENSION_SUFFIXES = '.ipynb',
    def __init__(self, fullname=None, path=None):
        super().__init__(fullname, path)
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


# In[ ]:


class Partial(Notebook):
    def exec_module(loader, module):
        try: super().exec_module(module)
        except BaseException as exception:
            try: raise ImportWarning(f"""{module.__name__} from {module.__file__} failed to load completely.""")
            except ImportWarning as error:
                print_exc()
                module.__exception__ = exception
        return module


# # IPython Extensions

# In[ ]:


def load_ipython_extension(ip=None): Notebook().__enter__()
def unload_ipython_extension(ip=None): Notebook().__exit__()


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
#             %rm test_loader.ipynb
        unload_ipython_extension()


# # Developer

# In[ ]:


if __name__ ==  '__main__':
#         __import__('doctest').testmod(verbose=2)
    __import__('unittest').TextTestRunner().run(Test())
    get_ipython().system('jupyter nbconvert --to script __init__.ipynb')


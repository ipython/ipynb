
# coding: utf-8

# # The [Import Loader](https://docs.python.org/3/reference/import.html#loaders)

# In[1]:


try:
    from .compiler import Compile, AST
except ModuleNotFoundError:
    from compiler import Compile, AST
import inspect, sys
from importlib.machinery import SourceFileLoader
from importlib._bootstrap_external import FileFinder
from importlib import reload
from traceback import print_exc


# In[2]:


def update_path_hooks(loader: SourceFileLoader, extensions: tuple=None, lazy=False):
    """Update the FileFinder loader in sys.path_hooks to accomodate a {loader} with the {extensions}"""
    from importlib.util import LazyLoader
    for id, hook in enumerate(sys.path_hooks):
        try:
            closure = inspect.getclosurevars(hook).nonlocals
        except TypeError: continue
        if issubclass(closure['cls'], FileFinder):
            sys.path_hooks.pop(id)
            sys.path_hooks.insert(id, FileFinder.path_hook(*(
                ((lazy and LazyLoader.factory(loader) or loader, extensions),) 
                if (loader and extensions) 
                else tuple()
            ) + tuple(
                (cls, ext) 
                for cls, ext in closure['loader_details'] 
                if not issubclass(cls, loader) # Need to add logic for lazy loaders before they may be introduced.
            )))
    sys.path_importer_cache.clear()


# In[3]:


class ImportContextMixin:
    def __enter__(self):  update_path_hooks(type(self), self.EXTENSION_SUFFIXES)
    def __exit__(self, exception_type=None, exception_value=None, traceback=None): update_path_hooks(type(self))


# In[4]:


class Notebook(SourceFileLoader, ImportContextMixin):
    """A SourceFileLoader for notebooks that provides line number debugginer in the JSON source."""
    EXTENSION_SUFFIXES = '.ipynb',
    
    def __init__(self, fullname=None, path=None): super().__init__(fullname, path)
    
    def exec_module(Loader, module):
        from IPython.utils.capture import capture_output    
        with capture_output(stdout=False, stderr=False) as output: 
            try: super().exec_module(module)
            except: ...
            finally: module.__output__ = output
        return module

    def source_to_code(Notebook, data, path):
        with __import__('io').BytesIO(data) as stream:
            return Compile().from_file(stream, filename=Notebook.path, name=Notebook.name)


# In[5]:


class Partial(Notebook):
    def exec_module(loader, module):
        try: super().exec_module(module)
        except BaseException as exception:
            try: raise ImportWarning("""{name} from {file} failed to load completely.""".format(
                name=module.__name__, file=module.__file__
            ))
            except ImportWarning as error:
                print_exc()
                module.__exception__ = exception
        return module


# # IPython Extensions

# In[6]:


def load_ipython_extension(ip=None): Notebook().__enter__()
def unload_ipython_extension(ip=None): Notebook().__exit__()


# In[7]:


class Test(__import__('unittest').TestCase): 
    def setUp(Test):
        from nbformat import write, v4
        load_ipython_extension()
        with open('test_loader.ipynb', 'w') as file:
            write(v4.new_notebook(cells=[
                v4.new_code_cell("""__import__("time").sleep(1);test = 42""")
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

# In[8]:


if __name__ ==  '__main__':
#         __import__('doctest').testmod(verbose=2)
#         __import__('unittest').TextTestRunner().run(Test())
    get_ipython().system('jupyter nbconvert --to script --TemplateExporter.exclude_input_prompt=True __init__.ipynb')
    with Notebook():
        import test_failure


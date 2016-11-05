"""
FileSystem based importer for ipynb / .py files.

If you prefix module names with 'ipynb.fs', it'll try to treat them exactly
the same way as .py files. All the output is ignored, and all the code is imported
as if the cells were linearly written to be in a flat file.
"""
import sys
import os

from importlib.abc import MetaPathFinder, Loader
from importlib.machinery import ModuleSpec

from ipynb.utils import get_code


class FSLoader(MetaPathFinder, Loader):
    """
    Finder & Loader for ipynb/py files from the filesystem.

    Only tries to load modules that are under ipynb.fs.
    Tries to treat .ipynb and .py files exactly the same as much as possible.
    """
    def _get_paths(self, fullname):
        """
        Generate ordered list of paths we should look for fullname module in
        """
        real_path = os.path.join(*fullname[len(__package__):].split('.'))
        for base_path in sys.path:
            if base_path == '':
                # Empty string means process's cwd
                base_path = os.getcwd()
            path = os.path.join(base_path, real_path)
            yield path + '.ipynb'
            yield path + '.py'
            yield os.path.join(path, '__init__.ipynb')
            yield os.path.join(path, '__init__.py')

    def get_source(self, fullname):
        for path in self._get_paths(fullname):
            try:
                with open(path) as f:
                    return get_code(f, path.endswith('.ipynb'))
            except FileNotFoundError:
                continue
        # If none of our paths match, fail the import!
        raise ImportError('Could not import {name}'.format(name=fullname))

    def get_code(self, fullname):
        return compile(self.get_source(fullname), '<string>', 'exec', dont_inherit=True)

    def exec_module(self, module):
        """
        """
        exec(self.get_source(module.__name__), module.__dict__)

    def find_spec(self, fullname, path, target=None):
        """
        Claims modules that are under ipynb.fs
        """
        if fullname.startswith(__package__):
            subpath = fullname[len(__package__):].replace(' ', '_')
            base_path = os.path.abspath(os.path.join(*subpath.split('.')))
            return ModuleSpec(
                name=fullname,
                loader=self,
                origin='ipynb.fs',
                is_package=os.path.isdir(base_path)
            )

sys.meta_path.append(FSLoader())

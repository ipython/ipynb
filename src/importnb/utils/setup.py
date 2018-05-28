# coding: utf-8
"""It is important to distribute notebooks in packages during the initial stages of code development.  This notebook creates a setuptools command class that allows for both python and notebook imports.  This was specifically created to allow notebooks as py_module imports, but could serve a greater purpose.
"""

"""    class BuildWithNotebooks(setuptools.command.build_py.build_py):
        def __new__(cls, distribution):
            from importnb.utils.setup import build_ipynb
            return build_ipynb(distribution)
    setup_args.update(cmdclass=dict(build_py=BuildWithNotebooks))

"""

from setuptools.command.build_py import build_py
import sys, os
from pathlib import Path
import importlib


class build_ipynb(build_py):
    """Should really use manifest.in

    Lazy import build_ipynb in your setup.

    class BuildWithNotebooks(setuptools.command.build_py.build_py):
        def __new__(cls, distribution):
            from importnb.utils.setup import build_ipynb
            return build_ipynb(distribution)
    setup_args.update(cmdclass=dict(build_py=BuildWithNotebooks))
    """

    def get_module_outfile(self, build_dir, package, module):
        module_mapper = {module[1]: module[2] for module in self.find_all_modules()}
        outfile_path = [build_dir] + list(package) + [module_mapper[module]]
        return os.path.join(*outfile_path)

    def find_package_modules(self, package, package_dir):
        from glob import glob

        self.check_package(package, package_dir)
        module_files = glob(os.path.join(package_dir, "*.py"))
        modules = []
        setup_script = os.path.abspath(self.distribution.script_name)

        for f in module_files + glob(os.path.join(package_dir, "*.ipynb")):
            abs_f = os.path.abspath(f)
            if abs_f != setup_script:
                module = os.path.splitext(os.path.basename(f))[0]
                modules.append((package, module, f))
            else:
                self.debug_print("excluding %s" % setup_script)
        return modules

    def find_modules(self):
        packages, modules = {}, []

        for module in self.py_modules:
            path = module.split(".")
            package = ".".join(path[0:-1])
            module_base = path[-1]

            try:
                (package_dir, checked) = packages[package]
            except KeyError:
                package_dir = self.get_package_dir(package)
                checked = 0

            if not checked:
                init_py = self.check_package(package, package_dir)
                packages[package] = (package_dir, 1)
                if init_py:
                    modules.append((package, "__init__", init_py))

            module_file = os.path.join(package_dir, module_base + ".ipynb")

            if Path(module_file).exists():
                modules.append((package, module_base, str(module_file)))
            else:
                module_file = str(Path(module_file).with_suffix(".py"))
                if self.check_module(module, module_file):
                    modules.append((package, module_base, str(module_file)))

        return modules


if __name__ == "__main__":
    try:
        from ..loader import export
    except:
        from importnb.loader import export
    export("setup.ipynb", "../../utils/setup.py")

try:
    from .. import exporter
except:
    import importnb.exporter

from setuptools.command.build_py import build_py
import sys, os
from pathlib import Path
import importlib


class build_ipynb(build_py):

    def get_module_outfile(self, build_dir, package, module):
        module_mapper = {module[1]: module[2] for module in self.find_all_modules()}
        outfile_path = [build_dir] + list(package) + [module_mapper[module]]
        return os.path.join(*outfile_path)

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
    from pathlib import Path

    try:
        from ..compiler_python import ScriptExporter
    except:
        from importnb.compiler_python import ScriptExporter

    Path("../../importnb/utils/setup.py").write_text(
        ScriptExporter().from_filename("setup.ipynb")[0]
    )

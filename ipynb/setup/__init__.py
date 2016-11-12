"""
Provides helpers to produce python packages sourced from .ipynb files
"""
from setuptools import PackageFinder
import os
import glob
import json
from ..utils import code_from_ipynb


class IPynbPackageFinder(PackageFinder):
    """
    A setuptools PackageFinder that provides .py files for .ipynb files when packaged
    """
    @staticmethod
    def _looks_like_package(path):
        like_package = os.path.isfile(os.path.join(path, '__init__.py'))
        like_package = like_package or os.path.isfile(os.path.join(path, '__init__.ipynb'))
        if like_package:
            ipynbs = glob.glob(os.path.join(path,'*.ipynb'))
            for ipynb in ipynbs:
                with open(ipynb) as notebook:
                    data = json.load(notebook)
                with open(ipynb.replace('ipynb','py'), 'w') as pyfile:
                    pyfile.write(code_from_ipynb(data, markdown=True))

        return like_package

find_packages = IPynbPackageFinder.find

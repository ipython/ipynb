from setuptools import PackageFinder
import os
import glob
from ..utils import get_code


class IPynbPackageFinder(PackageFinder):

    @staticmethod
    def _looks_like_package(path):
        like_package = os.path.isfile(os.path.join(path, '__init__.py'))
        like_package =  like_package or os.path.isfile(os.path.join(path, '__init__.ipynb'))
        if like_package:
            ipynbs = glob.glob(os.path.join(path,'*.ipynb'))
            for ipynb in ipynbs:
                with open(ipynb) as notebook:
                    data = notebook.read()
                with open(ipynb.replace('ipynb','py'), 'w') as pyfile:
                    pyfile.write(get_code(data, markdown=True))

        return like_package

find_packages = IPynbPackageFinder.find


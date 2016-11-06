.. ipynb documentation master file, created by
   sphinx-quickstart on Sun Nov  6 09:25:24 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ipynb's documentation!
=================================

This module allow you to import ``ipynb`` as is they were classical python
modules. Simply prepend ``ipynb.fs.`` to the regular import.

The `Zen of Python <https://www.python.org/dev/peps/pep-0020/>`_ say it well:
Explicit is better than implicit. Thus wile import-hook are useful they lack
explicitness. This module is meant to fix this by allowing you to explicitly
requiring notebook files.

This module does install an import kook, though it will only try to load
packages that explicitly start with `ipynb.fs.`

This is still highly work in progress, any feedback and improvement welcomed.


Contents:

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


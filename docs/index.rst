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
packages that explicitly start with ``ipynb.fs.``.

This is still highly work in progress, any feedback and improvement welcomed.

The source code for this package can be found
`on GitHub <https://github.com/yuvipanda/ipynb>`_.



Installation
============

To install this package you can use `pip <https://pypi.python.org/pypi/pip>`
that should be available with your python distribution. Use the following at
command prompt:

.. code::

    $ pip install ipynb --upgrade

Make sure to use a recent version of pip !

``ipynb`` requires python 3.4 or above to work. It is technically possible to
have it work on older python versions but might require quite some work. We
would welcome your contributions.


Developer install
-----------------

If you are developing the ``ipynb`` package, we suggest you do a developer install.
After cloning the source code, from the root of the newly clone directory issue a:

.. code::

    $ pip install -e .


How does ``ipynb`` work
=======================

The ``ipynb`` package setup an `importhook
<https://docs.python.org/3/reference/import.html>`_ which will automatically
make available as a python module any ``.ipynb`` files as long as the import
starts with ``ipynb.fs.``.


Limitation
==========

Although ``ipynb`` files are often connected to IPython kernel, ``ipynb`` does
not (yet?) support  many of IPython syntactic features like ``!shell command``
as well as line magics (``%magic``) and cell magics (``%%cell_magic``) While
the former should be pretty easy to emulate, the two later one requires the
code to be ran from with the main namespace of IPython so are unavailable.


FSdefs
======


Import using ``ipynb.fsdefs`` does not trigger side effects. 




Contents:

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. ipynb documentation master file, created by
   sphinx-quickstart on Sun Nov  6 09:25:24 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ipynb's documentation!
=================================

This module allow you to import ``ipynb`` as is they were classical python
modules. Simply prepend ``ipynb.fs.full`` to the regular import.

The `Zen of Python <https://www.python.org/dev/peps/pep-0020/>`_ say it well:
Explicit is better than implicit. Thus wile import-hook are useful they lack
explicitness. This module is meant to fix this by allowing you to explicitly
requiring notebook files.

This module does install an import hook, though it will only try to load
packages that explicitly start with ``ipynb.fs.``.

This is still highly work in progress, any feedback and improvement welcomed.

The source code for this package can be found
`on GitHub <https://github.com/ipython/ipynb>`_.



Installation
============

To install this package you can use `pip <https://pypi.python.org/pypi/pip>`
that should be available with your python distribution. Use the following at
command prompt:

.. code::

    $ pip install ipynb --upgrade

Make sure to use a recent version of pip!

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
as well as line magics (``%magic``) and cell magics (``%%cell_magic``). While
the former should be pretty easy to emulate, the two later one requires the
code to be ran from with the main namespace of IPython so are unavailable.


Import only definitions
=======================

If you would like to import only class & function definitions from a notebook
(and not the top level statements), you can use ``ipynb.fs.defs`` instead of
``ipynb.fs.full``. Full uppercase variable assignment will get evaluated as well.


Releasing a package that contains notebook files
================================================

You might have the need to release a python package with some modules written
as ``.ipynb`` files, but you do not want to require the  ``ipynb`` package.

If you are using `setuptools`, you can import `ipynb.setup.find_packages`,
which will convert ``.ipynb`` files to python files on before building an
source distribution or a wheel.

.. code::
    :file: setup.py

    from ipynb.setup import find_packages
    from setuptools import setup

    setup(
        name='trombulator',
        version='4.8.15162342',
        description='Trombulate with class using trombulator',
        url='http://tronbula.tor/',
        author='Rick Sanchez',
        author_email='morty@lubalubadub.dub',
        license='BSD',
        packages=find_packages(),
        python_requires='>=3.4'
    )




Contents:

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


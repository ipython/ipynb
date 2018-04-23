
Load the **importnb** to import notebooks.

|Binder|\ |Build Status|

.. |Binder| image:: https://mybinder.org/badge.svg
   :target: https://mybinder.org/v2/gh/deathbeds/importnb/master?filepath=readme.ipynb
.. |Build Status| image:: https://travis-ci.org/deathbeds/importnb.svg?branch=master
   :target: https://travis-ci.org/deathbeds/importnb

Jupyter Extension
-----------------

.. code:: ipython3

        if __name__ == '__main__':
            %reload_ext importnb
            import readme
            assert readme.foo is 42
            assert readme.__file__.endswith('.ipynb')
        else: 
            foo = 42
            

Notebooks maybe reloaded with the standard Python Import machinery.

.. code:: ipython3

        if __name__ == '__main__':
            from importnb import Notebook, reload
            reload(readme)
            %unload_ext importnb

Context Manager
---------------

.. code:: ipython3

        if __name__ == '__main__':
            try:  
                reload(readme)
                assert None, """Reloading should not work when the extension is unloaded"""
            except AttributeError: 
                with Notebook(): 
                    reload(readme)

Developer
---------

.. code:: ipython3

        if __name__ == '__main__':
            !jupyter nbconvert --to markdown readme.ipynb
            !jupyter nbconvert --to rst readme.ipynb


.. parsed-literal::

    [NbConvertApp] Converting notebook readme.ipynb to markdown
    [NbConvertApp] Writing 1280 bytes to readme.md


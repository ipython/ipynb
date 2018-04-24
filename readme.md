
__importnb__ supports the ability to use Jupyter notebooks as python source.

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/deathbeds/importnb/master?filepath=readme.ipynb)[![Build Status](https://travis-ci.org/deathbeds/importnb.svg?branch=master)](https://travis-ci.org/deathbeds/importnb)

    pip install importnb

## Jupyter Extension


```python
    if __name__ == '__main__':
        %reload_ext importnb
        import readme
        assert readme.foo is 42
        assert readme.__file__.endswith('.ipynb')
    else: 
        foo = 42
        
```

Notebooks maybe reloaded with the standard Python Import machinery.


```python
    if __name__ == '__main__':
        from importnb import Notebook, reload
        reload(readme)
        %unload_ext importnb
```

## Context Manager


```python
    if __name__ == '__main__':
        try:  
            reload(readme)
            assert None, """Reloading should not work when the extension is unloaded"""
        except AttributeError: 
            with Notebook(): 
                reload(readme)
```

## Developer


```python
    if __name__ == '__main__':
        !source activate p6 && ipython -m unittest discover
        !jupyter nbconvert --to markdown readme.ipynb
```

    EEEx.E
    ======================================================================
    ERROR: test_import (tests.unittests.TestContext)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/Users/tonyfast/importnb/tests/unittests.ipynb", line 47, in setUp
        "            with Notebook(): Test.loader = __import__('.loader')\n",
    ModuleNotFoundError: No module named '.loader'
    
    ======================================================================
    ERROR: test_reload_with_context (tests.unittests.TestContext)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/Users/tonyfast/importnb/tests/unittests.ipynb", line 47, in setUp
        "            with Notebook(): Test.loader = __import__('.loader')\n",
    ModuleNotFoundError: No module named '.loader'
    
    ======================================================================
    ERROR: test_reload_without_context (tests.unittests.TestContext)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/Users/tonyfast/importnb/tests/unittests.ipynb", line 47, in setUp
        "            with Notebook(): Test.loader = __import__('.loader')\n",
    ModuleNotFoundError: No module named '.loader'
    
    ======================================================================
    ERROR: test_exception (tests.unittests.TestPartial)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/Users/tonyfast/importnb/tests/unittests.ipynb", line 72, in setUp
        "                Test.failure = __import__('.failure')\n",
    ModuleNotFoundError: No module named '.failure'
    
    ----------------------------------------------------------------------
    Ran 6 tests in 1.019s
    
    FAILED (errors=4, expected failures=1)
    ]0;IPython: tonyfast/importnb[0;31m---------------------------------------------------------------------------[0m
    [0;31mSystemExit[0m                                Traceback (most recent call last)
    [0;32m~/anaconda/envs/p6/lib/python3.6/runpy.py[0m in [0;36mrun_module[0;34m(mod_name, init_globals, run_name, alter_sys)[0m
    [1;32m    203[0m         [0mrun_name[0m [0;34m=[0m [0mmod_name[0m[0;34m[0m[0m
    [1;32m    204[0m     [0;32mif[0m [0malter_sys[0m[0;34m:[0m[0;34m[0m[0m
    [0;32m--> 205[0;31m         [0;32mreturn[0m [0m_run_module_code[0m[0;34m([0m[0mcode[0m[0;34m,[0m [0minit_globals[0m[0;34m,[0m [0mrun_name[0m[0;34m,[0m [0mmod_spec[0m[0;34m)[0m[0;34m[0m[0m
    [0m[1;32m    206[0m     [0;32melse[0m[0;34m:[0m[0;34m[0m[0m
    [1;32m    207[0m         [0;31m# Leave the sys module alone[0m[0;34m[0m[0;34m[0m[0m
    
    [0;32m~/anaconda/envs/p6/lib/python3.6/runpy.py[0m in [0;36m_run_module_code[0;34m(code, init_globals, mod_name, mod_spec, pkg_name, script_name)[0m
    [1;32m     94[0m         [0mmod_globals[0m [0;34m=[0m [0mtemp_module[0m[0;34m.[0m[0mmodule[0m[0;34m.[0m[0m__dict__[0m[0;34m[0m[0m
    [1;32m     95[0m         _run_code(code, mod_globals, init_globals,
    [0;32m---> 96[0;31m                   mod_name, mod_spec, pkg_name, script_name)
    [0m[1;32m     97[0m     [0;31m# Copy the globals of the temporary module, as they[0m[0;34m[0m[0;34m[0m[0m
    [1;32m     98[0m     [0;31m# may be cleared when the temporary module goes away[0m[0;34m[0m[0;34m[0m[0m
    
    [0;32m~/anaconda/envs/p6/lib/python3.6/runpy.py[0m in [0;36m_run_code[0;34m(code, run_globals, init_globals, mod_name, mod_spec, pkg_name, script_name)[0m
    [1;32m     83[0m                        [0m__package__[0m [0;34m=[0m [0mpkg_name[0m[0;34m,[0m[0;34m[0m[0m
    [1;32m     84[0m                        __spec__ = mod_spec)
    [0;32m---> 85[0;31m     [0mexec[0m[0;34m([0m[0mcode[0m[0;34m,[0m [0mrun_globals[0m[0;34m)[0m[0;34m[0m[0m
    [0m[1;32m     86[0m     [0;32mreturn[0m [0mrun_globals[0m[0;34m[0m[0m
    [1;32m     87[0m [0;34m[0m[0m
    
    [0;32m~/anaconda/envs/p6/lib/python3.6/unittest/__main__.py[0m in [0;36m<module>[0;34m()[0m
    [1;32m     16[0m [0;32mfrom[0m [0;34m.[0m[0mmain[0m [0;32mimport[0m [0mmain[0m[0;34m,[0m [0mTestProgram[0m[0;34m[0m[0m
    [1;32m     17[0m [0;34m[0m[0m
    [0;32m---> 18[0;31m [0mmain[0m[0;34m([0m[0mmodule[0m[0;34m=[0m[0;32mNone[0m[0;34m)[0m[0;34m[0m[0m
    [0m
    [0;32m~/anaconda/envs/p6/lib/python3.6/unittest/main.py[0m in [0;36m__init__[0;34m(self, module, defaultTest, argv, testRunner, testLoader, exit, verbosity, failfast, catchbreak, buffer, warnings, tb_locals)[0m
    [1;32m     93[0m         [0mself[0m[0;34m.[0m[0mprogName[0m [0;34m=[0m [0mos[0m[0;34m.[0m[0mpath[0m[0;34m.[0m[0mbasename[0m[0;34m([0m[0margv[0m[0;34m[[0m[0;36m0[0m[0;34m][0m[0;34m)[0m[0;34m[0m[0m
    [1;32m     94[0m         [0mself[0m[0;34m.[0m[0mparseArgs[0m[0;34m([0m[0margv[0m[0;34m)[0m[0;34m[0m[0m
    [0;32m---> 95[0;31m         [0mself[0m[0;34m.[0m[0mrunTests[0m[0;34m([0m[0;34m)[0m[0;34m[0m[0m
    [0m[1;32m     96[0m [0;34m[0m[0m
    [1;32m     97[0m     [0;32mdef[0m [0musageExit[0m[0;34m([0m[0mself[0m[0;34m,[0m [0mmsg[0m[0;34m=[0m[0;32mNone[0m[0;34m)[0m[0;34m:[0m[0;34m[0m[0m
    
    [0;32m~/anaconda/envs/p6/lib/python3.6/unittest/main.py[0m in [0;36mrunTests[0;34m(self)[0m
    [1;32m    256[0m         [0mself[0m[0;34m.[0m[0mresult[0m [0;34m=[0m [0mtestRunner[0m[0;34m.[0m[0mrun[0m[0;34m([0m[0mself[0m[0;34m.[0m[0mtest[0m[0;34m)[0m[0;34m[0m[0m
    [1;32m    257[0m         [0;32mif[0m [0mself[0m[0;34m.[0m[0mexit[0m[0;34m:[0m[0;34m[0m[0m
    [0;32m--> 258[0;31m             [0msys[0m[0;34m.[0m[0mexit[0m[0;34m([0m[0;32mnot[0m [0mself[0m[0;34m.[0m[0mresult[0m[0;34m.[0m[0mwasSuccessful[0m[0;34m([0m[0;34m)[0m[0;34m)[0m[0;34m[0m[0m
    [0m[1;32m    259[0m [0;34m[0m[0m
    [1;32m    260[0m [0mmain[0m [0;34m=[0m [0mTestProgram[0m[0;34m[0m[0m
    
    [0;31mSystemExit[0m: True
    /Users/tonyfast/anaconda/envs/p6/lib/python3.6/site-packages/IPython/core/interactiveshell.py:2598: UserWarning: Unknown failure executing module: <unittest>
      warn('Unknown failure executing module: <%s>' % mod_name)
    [NbConvertApp] Converting notebook readme.ipynb to markdown
    [NbConvertApp] Writing 1262 bytes to readme.md


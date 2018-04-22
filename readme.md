
Load the __importnb__ to import notebooks.

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/deathbeds/importnb/master?filepath=readme.ipynb)


```python
    if __name__ == '__main__':
        %reload_ext importnb
    else: 
        foo = 42
        
    import readme
```


```python
    from importnb import Notebook, reload
```


```python
    try: 
        reload(readme)
    except AttributeError: 
        with Notebook():
            reload(readme)
```


```python
    if __name__ == '__main__':
        !jupyter nbconvert --to markdown readme.ipynb
```

    [NbConvertApp] Converting notebook readme.ipynb to markdown
    [NbConvertApp] Writing 699 bytes to readme.md


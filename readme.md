
Load the __importnb__ to import notebooks.

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/deathbeds/importnb/master?filepath=readme.ipynb)

## Jupyter Extension


```python
    if __name__ == '__main__':
        %reload_ext importnb
    else: 
        foo = 42
        
    import readme
    assert readme.__file__.endswith('.ipynb')
```

## Context Manager


```python
    from importnb import Notebook, reload

    try:  reload(readme)
    except AttributeError: 
        with Notebook(): reload(readme)
```

## Developer


```python
    if __name__ == '__main__':
        !jupyter nbconvert --to markdown readme.ipynb
```

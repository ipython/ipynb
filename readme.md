
Load the __importnb__ to import notebooks.


```python
    if __name__ == '__main__':
        %reload_ext importnb
    else: 
        foo = 42
```


```python
    import readme
    assert readme.__file__.endswith('ipynb')
    assert readme.foo is 42
```


```python
    if __name__ == '__main__':
        !jupyter nbconvert --to markdown readme.ipynb
```

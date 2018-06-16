# coding: utf-8
"""This is the docstring.
                
                >>> assert True
            

"""

foo = 42
assert foo
bar = 100

print(foo)

"""Markdown paragraph

"""

_repr_markdown_ = lambda: "a custom repr {foo}".format(foo=foo)

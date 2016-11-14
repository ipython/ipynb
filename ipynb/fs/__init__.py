"""
Module to enable relative & absolute import of .ipynb files.

This file in particular is useful to enable relative imports in
interactive notebook usage. None of the code executes outside
of an interactive notebook environment.

Relative imports require two things:
  - `__package__` is set
  - The module that is `__package__` is already imported

So we set __package__ in the notebook's namespace to the __package__
of this variable. This will allow users to do imports like:

```
from .full.notebook1 import foo
from .defs.notebook2 import bar
```

and they would work everywhere just fine.
"""
try:
    import IPython
    ip = IPython.get_ipython()

    if ip is not None:
        if ip.user_ns['__package__'] is None:
            ip.user_ns['__package__'] = __package__
except ImportError:
    # If we don't have IPython installed at all, let it go.
    # We aren't running in a jupyter notebook then.
    pass

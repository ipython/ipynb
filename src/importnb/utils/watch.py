
# coding: utf-8

"""# Watchdog for modules

Creates a module path from a source file to watch and execute file changes.

    tricks:
        patterns:
        - *.ipynb
        shell_command: ipython -m ${watch_dest_path}
        
"""


import os
from watchdog.tricks import ShellCommandTrick


class ModuleTrick(ShellCommandTrick):
    """ModuleTrick is a watchdog trick that """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ignore_patterns = self._ignore_patterns or []
        self._ignore_patterns.extend(("*-checkpoint.ipynb", "*.~*"))

    def on_any_event(self, event):
        try:
            event.dest_path = event.src_path.lstrip(".").lstrip(os.sep).rstrip(".ipynb").rstrip(
                ".py"
            ).replace(
                os.sep, "."
            )
            super().on_any_event(event)
        except AttributeError:
            ...


if __name__ == "__main__":
    from importnb.loader import export

    export("watch.ipynb", "../../importnb/utils/watch.py")

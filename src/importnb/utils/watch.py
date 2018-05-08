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
    try:
        from .compiler_python import ScriptExporter
    except:
        from importnb.compiler_python import ScriptExporter
    from pathlib import Path

    Path("../../importnb/utils/watch.py").write_text(
        ScriptExporter().from_filename("watch.ipynb")[0]
    )

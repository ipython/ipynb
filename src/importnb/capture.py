# coding: utf-8
"""# Python and IPython compatible stdout, stderr, and displays captures.
"""

try:
    from IPython.utils.capture import capture_output, CapturedIO
    from IPython import get_ipython

    assert get_ipython(), """There is no interactive shell"""
except:
    from contextlib import redirect_stdout, ExitStack
    from io import StringIO
    import sys

    try:
        from contextlib import redirect_stderr
    except:

        class redirect_stderr:

            def __init__(self, new_target):
                self._new_target = new_target
                self._old_targets = []

            def __enter__(self):
                self._old_targets.append(sys.stderr)
                sys.stderr = self._new_target
                return self._new_target

            def __exit__(self, exctype, excinst, exctb):
                sys.stderr = self._old_targets.pop()

    class capture_output(ExitStack):

        def __init__(self, stdout=True, stderr=True, display=True):
            self.stdout = stdout
            self.stderr = stderr
            self.display = display
            super().__init__()

        def __enter__(self):
            super().__enter__()
            stdout = stderr = outputs = None
            if self.stdout:
                stdout = StringIO()
                self.enter_context(redirect_stdout(stdout))
            if self.stderr:
                stderr = StringIO()
                self.enter_context(redirect_stderr(stderr))
            return CapturedIO(stdout, stderr, outputs)

    class CapturedIO:

        def __init__(self, stdout=None, stderr=None, outputs=None):
            self._stdout = stdout
            self._stderr = stderr
            self._outputs = self.outputs = outputs or []

        @property
        def stdout(self):
            return self._stdout and self._stdout.getvalue() or ""

        @property
        def stderr(self):
            return self._stderr and self._stderr.getvalue() or ""

        def show(self):
            """write my output to sys.stdout/err as appropriate"""
            sys.stdout.write(self.stdout)
            sys.stderr.write(self.stderr)
            sys.stdout.flush()
            sys.stderr.flush()


if __name__ == "__main__":
    try:
        from .utils.export import export
    except:
        from utils.export import export
    export("capture.ipynb", "../capture.py")
    __import__("doctest").testmod()


# coding: utf-8

try:
    from .compile import export, __IPYTHON__, export
except:
    from compile import export, __IPYTHON__, export
__all__ = "capture_output",


if __IPYTHON__:
    from IPython.utils.capture import capture_output
else:
    from contextlib import redirect_stdout, ExitStack
    from io import StringIO

    try:
        from contextlib import redirect_stderr
    except:
        import sys

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
            self.outputs = outputs

        @property
        def stdout(self):
            return self._stdout and self._stdout.getvalue() or ""

        @property
        def stderr(self):
            return self._stderr and self._stderr.getvalue() or ""


if __name__ == "__main__":
    export("capture.ipynb", "../importnb/capture.py")
    __import__("doctest").testmod()

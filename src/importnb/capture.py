try:
    from .utils import __IPYTHON__, export
except:
    from utils import __IPYTHON__, export

if False and __IPYTHON__:
    from IPython.utils.capture import capture_output
else:
    from contextlib import redirect_stderr, redirect_stdout, ExitStack
    from io import StringIO
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
        def stdout(self): return self._stdout and self._stdout.getvalue() or ''

        @property
        def stderr(self): return self._stderr and self._stderr.getvalue() or ''



if __name__ ==  '__main__':
    export('capture.ipynb', '../importnb/capture.py')
    __import__('doctest').testmod()
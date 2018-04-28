import pytest
try:
    from .loader import Notebook
except:
    from loader import Notebook

def pytest_collect_file(parent, path):
    if path.ext in ('.ipynb', '.py'):
        if not parent.session.isinitpath(path):
            for pat in parent.config.getini('python_files'):
                if path.fnmatch(pat.rstrip('.py') + path.ext):
                    break
            else:
                return
        return Module(path, parent)

class Module(pytest.Module):
    def collect(self):
        with Notebook(): 
            return super().collect()

if __name__ ==  '__main__':
    try:
        from .compiler_python import ScriptExporter
    except:
        from compiler_python import ScriptExporter
    from pathlib import Path
    Path('pytest_plugin.py').write_text(ScriptExporter().from_filename('pytest_plugin.ipynb')[0])
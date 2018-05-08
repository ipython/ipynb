__IPYTHON__ = False
try:
    try:
        from . import ipython
    except:
        import ipython
    if not ipython.get_ipython():
        raise ValueError("""There is no interactive IPython shell""")
    __IPYTHON__ = True
except: ...

from pathlib import Path

try:
    from ..compiler_python import ScriptExporter

except:
    from importnb.compiler_python import ScriptExporter

def export(src, dst):
    Path(dst).write_text(ScriptExporter().from_filename(src)[0])

if __name__ ==  '__main__':

    export('__init__.ipynb', '../../importnb/utils/__init__.py')
    export('__init__.ipynb', '__init__.py')
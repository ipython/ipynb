def install(profile="profile_default"):
    from IPython import get_ipython
    from IPython.core.magics.execution import ExecutionMagics
    from IPython.paths import get_ipython_dir

    from pathlib import Path

    startup = Path(get_ipython_dir()) / profile / "startup"
    startup.mkdir(exist_ok=True)
    script = startup / "importnb_startup.ipy"
    script.write_text("""%reload_ext importnb""")
    ExecutionMagics(get_ipython()).run(str(script))


def load_ipython_extension(ip):
    install()


if __name__ == "__main__":
    try:
        from .compiler_python import ScriptExporter
    except:
        from importnb.compiler_python import ScriptExporter
    from pathlib import Path

    Path("../../importnb/utils/ipython.py").write_text(
        ScriptExporter().from_filename("ipython.ipynb")[0]
    )

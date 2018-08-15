# coding: utf-8
from doctest import OPTIONFLAGS_BY_NAME, testfile, testmod, FAIL_FAST
import os, argparse

try:
    from ..loader import Notebook
except:
    from importnb import Notebook


def _test():
    parser = argparse.ArgumentParser(description="doctest runner")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="print very verbose output for all tests",
    )
    parser.add_argument(
        "-o",
        "--option",
        action="append",
        choices=OPTIONFLAGS_BY_NAME.keys(),
        default=[],
        help=(
            "specify a doctest option flag to apply"
            " to the test run; may be specified more"
            " than once to apply multiple options"
        ),
    )
    parser.add_argument(
        "-f",
        "--fail-fast",
        action="store_true",
        help=(
            "stop running tests after first failure (this"
            " is a shorthand for -o FAIL_FAST, and is"
            " in addition to any other -o options)"
        ),
    )
    parser.add_argument("file", nargs="+", help="file containing the tests to run")
    args = parser.parse_args()
    testfiles = args.file
    # Verbose used to be handled by the "inspect argv" magic in DocTestRunner,
    # but since we are using argparse we are passing it manually now.
    verbose = args.verbose
    options = 0
    for option in args.option:
        options |= OPTIONFLAGS_BY_NAME[option]
    if args.fail_fast:
        options |= FAIL_FAST
    for filename in testfiles:
        if any(map(filename.endswith, (".py", ".ipynb"))):
            # It is a module -- insert its dir into sys.path and try to
            # import it. If it is part of a package, that possibly
            # won't work because of package imports.
            failures, _ = testmod(Notebook.load(filename), verbose=verbose, optionflags=options)
        else:
            failures, _ = testfile(
                filename, module_relative=False, verbose=verbose, optionflags=options
            )
        if failures:
            return 1
    return 0


if __name__ == "__main__":
    _test()

if __name__ == "__main__":
    from .export import export

    export("nbdoctest.ipynb", "../../utils/nbdoctest.py")

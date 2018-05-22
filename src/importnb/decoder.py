
# coding: utf-8

"""# Decoding

If a notebook is imported, it should provide a natural __traceback__ experience similar to python imports.  The `importnb` importer creates a just decoder object that retains line numbers to the raw json when the notebook is imported.
"""


from functools import singledispatch
from json.decoder import JSONObject, JSONDecoder, WHITESPACE, WHITESPACE_STR
from json import load as _load, loads as _loads
from functools import partial

try:
    from IPython.core.inputsplitter import IPythonInputSplitter

    dedent = IPythonInputSplitter().transform_cell
except:
    from textwrap import dedent


def identity(*x):
    return x[0]


class LineNumberDecoder(JSONDecoder):
    """A JSON Decoder to return a NotebookNode with lines numbers in the metadata."""

    def __init__(
        self,
        *,
        object_hook=None,
        parse_float=None,
        parse_int=None,
        parse_constant=None,
        strict=True,
        object_pairs_hook=None
    ):
        from json.scanner import py_make_scanner

        super().__init__(
            object_hook=object_hook,
            parse_float=parse_float,
            parse_int=parse_int,
            parse_constant=parse_constant,
            strict=strict,
            object_pairs_hook=object_pairs_hook,
        )
        self.parse_object = self._parse_object
        self.scan_once = py_make_scanner(self)

    def _parse_object(
        self,
        s_and_end,
        strict,
        scan_once,
        object_hook,
        object_pairs_hook,
        memo=None,
        _w=WHITESPACE.match,
        _ws=WHITESPACE_STR,
    ) -> (dict, int):
        object, next = JSONObject(
            s_and_end, strict, scan_once, object_hook, object_pairs_hook, memo=memo, _w=_w, _ws=_ws
        )
        if "cell_type" in object:
            object["metadata"].update(
                {"lineno": len(s_and_end[0][:next].rsplit('"source":', 1)[0].splitlines())}
            )

            if object["cell_type"] == "markdown":
                object["source"] = codify_markdown(object["source"])
                object["outputs"] = []
                object["cell_type"] = "code"
                object["execution_count"] = None

        for key in ("source", "text"):
            if key in object:
                object[key] = "".join(object[key])

        return object, next


@singledispatch
def codify_markdown(string_or_list):
    raise TypeError("Markdown must be a string or a list.")


@codify_markdown.register(str)
def codify_markdown_string(str):
    if '"""' in str:
        str = "'''{}\n'''".format(str)
    else:
        str = '"""{}\n"""'.format(str)
    return str


@codify_markdown.register(list)
def codify_markdown_list(str):
    return list(map("{}\n".format, codify_markdown_string("".join(str)).splitlines()))


load = partial(_load, cls=LineNumberDecoder)
loads = partial(_loads, cls=LineNumberDecoder)


def transform_cells(object, transform=dedent):
    for cell in object["cells"]:
        if "source" in cell:
            cell["source"] = transform("".join(cell["source"]))
    return object


def ast_from_cells(object, transform=identity):
    import ast

    module = ast.Module(body=[])
    for cell in object["cells"]:
        module.body.extend(
            ast.fix_missing_locations(
                ast.increment_lineno(
                    ast.parse("".join(cell["source"])), cell["metadata"].get("lineno", 1)
                )
            ).body
        )
    return module


def loads_ast(object, loads=loads, transform=dedent, ast_transform=identity):
    if isinstance(object, str):
        object = loads(object)
    object = transform_cells(object, transform)
    return ast_from_cells(object, ast_transform)


if __name__ == "__main__":
    try:
        from .utils.export import export
    except:
        from utils.export import export
    export("decoder.ipynb", "../decoder.py")

    __import__("doctest").testmod()

# coding: utf-8
"""# Decode `nbformat` with line numbers

`importnb` decodes notebooks with the `nbformat` in valid source code.

We consider three kinds of cells.
"""

from json.decoder import JSONObject, JSONDecoder, WHITESPACE, WHITESPACE_STR
from json import load as _load, loads as _loads
from functools import partial
from json.scanner import py_make_scanner
from json.decoder import JSONDecoder, WHITESPACE, WHITESPACE_STR, JSONObject, py_scanstring
import linecache, textwrap

"""Output the strings slice that the source came from.
"""


def scanstring(s, end, strict=True, **kwargs):
    s, id = py_scanstring(s, end, strict, **kwargs)
    return (slice(end, id), s), id


def quote(object, *, quotes="'''"):
    if quotes in object:
        quotes = '"""'
    return quotes + object + "\n" + quotes


def object_pairs_hook(object) -> (slice, str):
    object = dict(object)
    if "cells" in object:
        return object["cells"]

    if "cell_type" in object:
        _, object["cell_type"] = object["cell_type"]

    for key in ["text", "source"]:
        if key in object:
            if object[key]:
                return (
                    slice(object[key][0][0].start, object[key][-1][0].stop),
                    object,
                    "".join(_[1] for _ in object[key]),
                )
    return slice(None), None, None


class LineCacheNotebookDecoder(JSONDecoder):
    def __init__(
        self,
        markdown=quote,
        code=textwrap.dedent,
        raw=partial(textwrap.indent, prefix="# "),
        **kwargs
    ):
        super().__init__(**kwargs)

        for key in ("markdown", "code", "raw"):
            setattr(self, "transform_" + key, locals().get(key))

        self.parse_string = scanstring
        self.object_pairs_hook = object_pairs_hook
        self.scan_once = py_make_scanner(self)

    def decode(self, object, filename):
        lines = []

        linecache.updatecache(filename)
        if filename in linecache.cache:
            linecache.cache[filename] = (
                linecache.cache[filename][0],
                linecache.cache[filename][1],
                lines,
                filename,
            )
        last, new, old = slice(0, 0), 0, 0
        for current, cell, source in super().decode(object):
            if cell:
                lines += ["\n"] * (
                    object[last.stop : current.start].splitlines().__len__() - 1 + (old - new)
                )

                source = getattr(self, "transform_" + cell["cell_type"])(source)

                lines += list(map("{}\n".format, source.splitlines()))
                new, old = map(len, map(str.splitlines, (source, object[current])))
                if not lines[-1]:
                    lines.pop()
                last = current

        return "".join(lines)


if __name__ == "__main__":
    try:
        from utils.export import export
    except:
        from .utils.export import export
    export("decoder.ipynb", "../decoder.py")

# coding: utf-8
from json.decoder import JSONObject, JSONDecoder, WHITESPACE, WHITESPACE_STR
from json import load as _load, loads as _loads
from functools import partial


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

        for key in ("source", "text"):
            if key in object:
                object[key] = "".join(object[key])

        return object, next


loads = partial(_loads, cls=LineNumberDecoder)

if __name__ == "__main__":
    try:
        from utils.export import export
    except:
        from .utils.export import export
    export("decoder.ipynb", "../decoder.py")

"""# More Information

The `importnb.loader` module recreates basic Python importing abilities.  Have a look at [`execute.ipynb`](execute.ipynb) for more advanced usages.
"""

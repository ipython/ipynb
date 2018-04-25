from json.decoder import JSONObject, JSONDecoder, WHITESPACE, WHITESPACE_STR


class LineNoDecoder(JSONDecoder):
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
        self.parse_object = self.object
        self.scan_once = py_make_scanner(self)

    def object(
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


if __name__ == "__main__":
    from pathlib import Path
    from nbconvert.exporters.script import ScriptExporter

    Path("decoder.py").write_text(ScriptExporter().from_filename("decoder.ipynb")[0])
    __import__("doctest").testmod()

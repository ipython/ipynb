import json


def get_code(data, parse_notebook):
    """
    Execute contents of a given stream in a given module

    data is a file-like object that'll be read from for contents
    module is the module in which to execute this code
    parse_notebok is a bool, set to True to parse `data` as a notebook rather
    than as a simple python file

    FIXME: If you use any ipython magics here, it'll go boom.
    """
    if parse_notebook:
        nb = json.load(data)

        code = ''
        for cell in nb['cells']:
            if cell['cell_type'] == 'code':
                # transform the input to executable Python
                code += '\n'.join(cell['source'])
                code += '\n'
        return code
    else:
        return data.read()

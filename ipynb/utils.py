import json


def get_code(data):
    """
    Execute contents of a given stream in a given module

    data is a file-like object that'll be read from for contents
    module is the module in which to execute this code

    FIXME: If you use any ipython magics here, it'll go boom.
    """
    nb = json.loads(data)

    code = ''
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            # transform the input to executable Python
            code += '\n'.join(cell['source'])
            code += '\n'
    return code

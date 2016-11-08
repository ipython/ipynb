import json

PREAMBLE=\
"""
##############################################################################
# This source has been auto generated from an IPython/Jupyter notebook file. #
# Please modify the origin file                                              #
##############################################################################
"""


def get_code(data, markdown=False):
    """
    Execute contents of a given stream in a given module

    data is a file-like object that'll be read from for contents
    module is the module in which to execute this code

    FIXME: If you use any IPython magics here, it'll go boom.
    """
    nb = json.loads(data)

    code = PREAMBLE
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            # transform the input to executable Python
            code += '\n'.join(cell['source'])
            code += '\n'
        if cell['cell_type'] == 'markdown':
            code += '\n' +'\n# '.join(cell['source'])
    return code

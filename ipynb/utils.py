PREAMBLE=\
"""
##############################################################################
# This source has been auto generated from an IPython/Jupyter notebook file. #
# Please modify the origin file                                              #
##############################################################################
"""

def validate_nb(nb):
    """
    Validate that given notebook JSON is importable

    - Check for nbformat == 4
    - Check that language is python3

    Do not re-implement nbformat here :D
    """
    return nb['nbformat'] == 4 and nb['metadata']['kernelspec']['name'] == 'python3'


def get_code(nb, markdown=False):
    """
    Get the code for a given notebook

    nb is passed in as a dictionry that's a parsed ipynb file
    """
    code = PREAMBLE
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            # transform the input to executable Python
            code += '\n'.join(cell['source'])
            code += '\n'
        if cell['cell_type'] == 'markdown':
            code += '\n' +'\n# '.join(cell['source'])
    return code

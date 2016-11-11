"""
Utility functions for dealing with manipulating notebooks.

Try to not put too many things here, nor to re-implement nbformat.
"""

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
    - Check that language is python

    Do not re-implement nbformat here :D
    """
    if nb['nbformat'] != 4:
        return False

    language_name = (nb.get('metadata', {})
        .get('kernelspec', {})
        .get('language', '').lower())
    return language_name == 'python'


def code_from_ipynb(nb, markdown=False):
    """
    Get the code for a given notebook

    nb is passed in as a dictionary that's a parsed ipynb file
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

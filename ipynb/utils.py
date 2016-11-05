import nbformat
from IPython import get_ipython
from IPython.core.interactiveshell import InteractiveShell


def get_code(data, parse_notebook):
    """
    Execute contents of a given stream in a given module

    data is a file-like object that'll be read from for contents
    module is the module in which to execute this code
    parse_notebok is a bool, set to True to parse `data` as a notebook rather
    than as a simple python file
    """
    if parse_notebook:
        nb = nbformat.read(data, as_version=4)
        shell = InteractiveShell.instance()

        code = ''
        for cell in nb.cells:
            if cell.cell_type == 'code':
                # transform the input to executable Python
                code += shell.input_transformer_manager.transform_cell(cell.source)
        return code
    else:
        return data.read()

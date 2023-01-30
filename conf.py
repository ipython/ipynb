project = 'importnb'
copyright = '2018, deathbeds'
author = 'deathbeds'

version = release = '0.5.0'

extensions = ['nbsphinx', 'sphinx.ext.autodoc', 'sphinx.ext.doctest', 'sphinx.ext.intersphinx',
                  'sphinx.ext.coverage', 'sphinx.ext.viewcode']

templates_path = ['docs/_includes']
source_suffix = '.ipynb'

master_doc = 'index'
exclude_patterns = [
    '*.ipynb_checkpoints*', '.eggs*', '.tox*', 'build', 'dist', '_build', 'Thumbs.db', '.DS_Store']

pygments_style = 'sphinx'
html_theme = 'alabaster'
html_static_path = ['docs']

htmlhelp_basename = 'importnbdoc'
latex_elements = {}

latex_documents = [
    (master_doc, 'importnb.tex', 'importnb Documentation',
     'deathbeds', 'manual'),
]
man_pages = [
    (master_doc, 'importnb', 'importnb Documentation',
     [author], 1)]
texinfo_documents = [
    (master_doc, 'importnb', 'importnb Documentation',
     author, 'importnb', 'One line description of project.',
     'Miscellaneous')]
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright
epub_exclude_files = ['search.html']
intersphinx_mapping = {'https://docs.python.org/': None}
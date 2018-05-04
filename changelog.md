
## CHANGELOG

# 0.2.4

* Use `tox` for testing
* Use a source directory folder structure for pytest and tox testing.
* Create a pytest plugin that discovers notebooks as tests.  With `importnb` notebooks can be used as fixtures in pytest.
* Install `importnb` as an IPython extension.
* Support running notebooks as modules from the `ipython` command line
* Create a `setuptools` command to allow notebooks as packages. 

# 0.2.1

* `importnb` supports notebook inputs from pure python environments.  Two compatible compiler were created from IPython and Python
* `importnb.Partial` works appropriately by improving exceptions.
* All of the IPython magic syntaxes were removed to support Pure Python.
* The generated Python files are formatted with black.
* Tests were added to:

    * Validate the line number in tracebacks
    * Test someone elses notebooks

### 0.1.4
- Pypi supports markdown long_description with the proper mimetype in long_description_content_type.

### 0.1.3
- Include the RST files in the `MANIFEST.in`.

### 0.1.2 (Unreleased)
- Use RST files to improve the literacy of the pypi description.

### 0.1.1
- Released on PyPi 

### 0.0.2
- Initial Testing Release

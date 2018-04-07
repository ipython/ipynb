__import__('setuptools').setup(
    name="importnb",
    version="0.0.1",
    author="deathbeds", author_email="tony.fast@gmail.com",
    description="Import notebook in the system path.", 
    license="BSD-3-Clause",
    install_requires=[],
    include_package_data=True,
    packages=__import__('setuptools').find_packages(),
)
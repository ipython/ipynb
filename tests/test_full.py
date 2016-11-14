import pytest
import importlib


@pytest.fixture(
    scope='module',
    params=[
        'ipynb.fs.full.pure_ipynb.foo',
        'ipynb.fs.full.mixed_ipynb.foo'
    ]
)
def mod(request):
    return importlib.import_module(request.param)

def test_execute(mod):
    assert mod.foo() == 'foo'
    assert mod.bar == 'hi'
    assert mod.r.rawr() == 'rawr'

def test_allcaps_execute(mod):
    assert mod.WAT == 'boo'

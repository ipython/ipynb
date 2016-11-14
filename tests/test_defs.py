import pytest
import importlib


@pytest.fixture(
    scope='module',
    params=[
        'ipynb.fs.defs.pure_ipynb.foo',
        'ipynb.fs.defs.mixed_ipynb.foo'
    ]
)
def mod(request):
    return importlib.import_module(request.param)

def test_execute(mod):
    assert mod.foo() == 'foo'
    rawr = mod.RAWR()
    assert rawr.rawr() == 'rawr'

def test_no_execute(mod):
    assert not hasattr(mod, 'bar')
    assert not hasattr(mod, 'r')

def test_allcaps_execute(mod):
    assert mod.WAT == 'boo'


import pytest
import importlib


@pytest.fixture(
    scope='module',
    params=[
        'ipynb.fs.defs.pure_ipynb.foo',
        'ipynb.fs.defs.mixed_ipynb.foo'
    ]
)
def foo(request):
    return importlib.import_module(request.param)

@pytest.fixture(
    scope='module',
    params=[
        'ipynb.fs.defs.pure_ipynb',
        'ipynb.fs.defs.mixed_ipynb'
    ]
)
def init(request):
    return importlib.import_module(request.param)

def test_execute(foo):
    assert foo.foo() == 'foo'
    rawr = foo.RAWR()
    assert rawr.rawr() == 'rawr'

def test_no_execute(foo):
    assert not hasattr(foo, 'bar')
    assert not hasattr(foo, 'r')

def test_allcaps_execute(foo):
    assert foo.WAT == 'boo'

def test_all(init):
    r = init.RAWR()
    assert r.rawr() == 'rawr'

import pytest
import importlib


@pytest.fixture(
    scope='module',
    params=[
        'ipynb.fs.full.pure_ipynb.foo',
        'ipynb.fs.full.mixed_ipynb.foo'
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
    assert foo.bar == 'hi'
    assert foo.r.rawr() == 'rawr'

def test_allcaps_execute(foo):
    assert foo.WAT == 'boo'

def test_all(init):
    r = init.RAWR()
    assert r.rawr() == 'rawr'

def test_bogus_ipynb():
    with pytest.raises(ImportError):
        import ipynb.fs.full.bogus_ipynb as bogus_ipynb

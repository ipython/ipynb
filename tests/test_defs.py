import ipynb.fs.defs.pure_ipynb as a
import ipynb.fs.defs.pure_ipynb.foo as foo


def test_a():
    assert a.init() == 'init'

def test_foo():
    assert foo.foo() == 'foo'
    rawr = foo.RAWR()
    assert rawr.rawr() == 'rawr'

def test_no_execute():
    assert not hasattr(foo, 'bar')

def test_allcaps_execute():
    assert foo.WAT == 'boo'


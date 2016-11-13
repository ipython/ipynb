import ipynb.fs.defs.a as a
import ipynb.fs.defs.a.foo as foo


def test_a():
    assert a.init() == 'init'

def test_foo():
    assert foo.foo() == 'foo'

def test_no_execute():
    assert not hasattr(foo, 'bar')


def test_allcaps_execute():
    assert foo.WAT == 'boo'

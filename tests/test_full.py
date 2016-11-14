import ipynb.fs.full.pure_ipynb as a
import ipynb.fs.full.pure_ipynb.foo as foo


def test_a():
    assert a.init() == 'init'

def test_foo():
    assert foo.foo() == 'foo'

def test_execute():
    assert foo.bar == 'hi'
    assert foo.r.rawr() == 'rawr'

def test_allcaps_execute():
    assert foo.WAT == 'boo'

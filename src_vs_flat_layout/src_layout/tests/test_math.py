from mypkg_src.math import add, subtract

def test_add():
    assert add(2, 3) == 5

def test_subtract():
    assert subtract(5, 3) == 2

def test_multiple():
    assert multiple(2, 5) == 10

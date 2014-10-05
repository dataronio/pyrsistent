import pickle
import pytest
from pyrsistent import plist, l


def test_literalish_works():
    assert l(1, 2, 3) == plist([1, 2, 3])


def test_first_and_rest():
    pl = plist([1, 2])
    assert pl.first == 1
    assert pl.rest.first == 2
    assert pl.rest.rest is plist()


def test_instantiate_large_list():
    assert plist(range(1000)).first == 0


def test_iteration():
    assert list(plist()) == []
    assert list(plist([1, 2, 3])) == [1, 2, 3]


def test_cons():
    assert plist([1, 2, 3]).cons(0) == plist([0, 1, 2, 3])


def test_cons_empty_list():
    assert plist().cons(0) == plist([0])


def test_truthiness():
    assert plist([1])
    assert not plist()


def test_len():
    assert len(plist([1, 2, 3])) == 3
    assert len(plist()) == 0


def test_first_illegal_on_empty_list():
    with pytest.raises(AttributeError):
        plist().first


def test_rest_illegal_on_empty_list():
    with pytest.raises(AttributeError):
        plist().rest


def test_reverse():
    assert plist([1, 2, 3]).reverse() == plist([3, 2, 1])
    assert reversed(plist([1, 2, 3])) == plist([3, 2, 1])

    assert plist().reverse() == plist()
    assert reversed(plist()) == plist()


def test_inequality():
    assert plist([1, 2]) != plist([1, 3])
    assert plist([1, 2]) != plist([1, 2, 3])
    assert plist() != plist([1, 2, 3])


def test_repr():
    assert str(plist()) == "plist([])"
    assert str(plist([1, 2, 3])) == "plist([1, 2, 3])"


def test_indexing():
    assert plist([1, 2, 3])[2] == 3
    assert plist([1, 2, 3])[-1] == 3
    assert plist


def test_indexing_on_empty_list():
    with pytest.raises(IndexError):
        plist()[0]

def test_slicing_take():
    assert plist([1, 2, 3])[:2] == plist([1, 2])


def test_slicing_drop():
    li = plist([1, 2, 3])
    assert li[1:] is li.rest


def test_contains():
    assert 2 in plist([1, 2, 3])
    assert 4 not in plist([1, 2, 3])
    assert 1 not in plist()


def test_count():
    assert plist([1, 2, 1]).count(1) == 2
    assert plist().count(1) == 0


def test_index():
    assert plist([1, 2, 3]).index(3) == 2


def test_index_item_not_found():
    with pytest.raises(ValueError):
        plist().index(3)

    with pytest.raises(ValueError):
        plist([1, 2]).index(3)


def test_pickling_empty_list():
    assert pickle.loads(pickle.dumps(plist(), -1)) == plist()


def test_pickling_non_empty_list():
    assert pickle.loads(pickle.dumps(plist([1, 2, 3]), -1)) == plist([1, 2, 3])


# Pickling
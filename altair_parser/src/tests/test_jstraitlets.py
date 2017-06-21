import pytest

import traitlets as T
from .. import jstraitlets as jst
from ..jstraitlets import undefined


def test_undefined_singleton():
    assert jst.UndefinedType() is undefined


def generate_test_cases():
    """yield tuples of (trait, failcases, passcases)"""
    yield (jst.JSONNull(), [0, "None"], [None])
    yield (jst.JSONBoolean(), [0, 2, 'abc'], [True, False])
    yield (jst.JSONNumber(), [None, '123'], [-10.5, 42, 3.14])
    yield (jst.JSONInteger(), [None, '123', 3.14], [-10, 0, 42])
    yield (jst.JSONString(), [50, None, True], ['abc'])
    yield (jst.JSONUnion([jst.JSONInteger(), jst.JSONString()]),
           [3.14, None], [42, "42"])
    yield (jst.JSONArray(jst.JSONString()),
           ["a", [1, 'b']], [["a", "b"], ['a']])
    yield (jst.JSONEnum([1, "2", None]), ["1", 2, [1]], [1, "2", None])
    yield (jst.JSONInstance(dict), [{1}, (1,), [1]], [{1:2}])
    yield (jst.JSONAnyOf([jst.JSONInteger(), jst.JSONString()]),
           [3.14, None], [42, "42"])
    yield (jst.JSONOneOf([jst.JSONInteger(), jst.JSONNumber()]),
           [None, 3], [3.14])
    yield (jst.JSONAllOf([jst.JSONInteger(), jst.JSONNumber()]),
           [None, 3.14], [3])
    yield (jst.JSONNot(jst.JSONString()), ['a', 'abc'], [1, False, None])


@pytest.mark.parametrize('trait,failcases,passcases', generate_test_cases())
def test_traits(trait, failcases, passcases):
    obj = T.HasTraits()  # needed to pass to validate()

    # All should validate undefined
    trait.validate(obj, undefined)

    for passcase in passcases:
        trait.validate(obj, passcase)

    for failcase in failcases:
        with pytest.raises(T.TraitError) as err:
            trait.validate(obj, failcase)

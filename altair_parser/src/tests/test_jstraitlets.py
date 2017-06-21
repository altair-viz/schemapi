import pytest

import traitlets as T

from ..jstraitlets import (undefined, UndefinedType, JSONNull,
                           JSONNumber, JSONString, JSONBoolean)


def test_undefined_singleton():
    assert UndefinedType() is undefined


@pytest.mark.parametrize('Trait,failcase,passcase',
                         [(JSONNull, 42, None), (JSONBoolean, 'abc', True),
                          (JSONNumber, None, 42), (JSONString, 50, 'abc')])
def test_traits(Trait, failcase, passcase):
    trait = Trait()
    obj = None

    trait.validate(obj, passcase)
    with pytest.raises(T.TraitError) as err:
        trait.validate(obj, failcase)
    assert trait.info_text in str(err)

import traitlets as T
from ..baseobject import BaseObject

class Bar(BaseObject):
    val = T.Unicode()

class Foo(BaseObject):
    x = T.Integer()
    y = T.Instance(Bar)

def test_baseobject():
    dct = {'x': 4, 'y': {'val': 'hello'}}
    obj = Foo.from_dict(dct)
    dct2 = obj.to_dict()
    assert dct == dct2

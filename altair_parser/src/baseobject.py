import traitlets as T
from .jstraitlets import undefined


class BaseObject(T.HasTraits):
    @classmethod
    def from_dict(cls, dct):
        obj = cls()
        for key, val in dct.items():
            trait = obj.traits()[key]
            if isinstance(trait, T.Instance) and issubclass(trait.klass, BaseObject):
                val = trait.klass.from_dict(val)
            obj.set_trait(key, val)
        return obj

    def to_dict(self):
        dct = {}
        for key in self.trait_names():
            val = getattr(self, key)
            if val is undefined:
                continue
            if isinstance(val, T.HasTraits):
                val = val.to_dict()
            dct[key] = val
        return dct

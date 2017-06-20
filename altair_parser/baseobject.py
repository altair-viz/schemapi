import traitlets as T


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

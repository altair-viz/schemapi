import traitlets as T
from .jstraitlets import undefined, DefaultHasTraits


class BaseObject(DefaultHasTraits):
    _default_trait = False

    @classmethod
    def from_dict(cls, dct):
        """Initialize an instance from a (nested) dictionary"""
        obj = cls()
        if not isinstance(dct, dict):
            raise T.TraitError("Argument to from_dict should be a dict, "
                               "but got {0}".format(dct))
        for key, val in dct.items():
            if isinstance(val, dict):
                trait = obj.traits()[key]
                subtraits = trait.trait_types if isinstance(trait, T.Union) else [trait]
                for subtrait in subtraits:
                    if isinstance(subtrait, T.Instance) and issubclass(subtrait.klass, BaseObject):
                        val = subtrait.klass.from_dict(val)
                        break
            obj.set_trait(key, val)
        return obj

    def to_dict(self):
        """Output a (nested) dict encoding the contents of this instance"""
        dct = {}
        for key in self.trait_names():
            val = getattr(self, key)
            if val is undefined:
                continue
            if isinstance(val, T.HasTraits):
                val = val.to_dict()
            dct[key] = val
        return dct

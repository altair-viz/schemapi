"""
Extensions to traitlets for use with JSON
"""
import traitlets as T


class UndefinedType(object):
    """A Singleton type to mark undefined traits"""
    __instance = None
    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.__instance, cls):
            cls.__instance = object.__new__(cls, *args, **kwargs)
        return cls.__instance
    def __repr__(self):
        return "undefined"
undefined = UndefinedType()


class JSONNull(T.TraitType):
    default_value = undefined
    info_text = 'a JSON null value'

    def validate(self, obj, value):
        if value is undefined or value is None:
            return value
        self.error(obj, value)


class JSONNumber(T.CFloat):
    default_value = undefined
    info_text = "a JSON number"

    def validate(self, obj, value):
        if value is undefined:
            return value
        return super().validate(obj, value)


class JSONString(T.Unicode):
    default_value = undefined
    info_text = "a JSON string"

    def validate(self, obj, value):
        if value is undefined:
            return value
        return super().validate(obj, value)


class JSONBoolean(T.Bool):
    default_value = undefined
    info_text = "a JSON boolean"

    def validate(self, obj, value):
        if value is undefined:
            return value
        return super().validate(obj, value)

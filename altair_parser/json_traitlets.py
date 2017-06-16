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
    allow_undefined = True
    default_value = undefined
    info_text = 'a JSON null value'

    def __init__(self, allow_undefined=True, **kwargs):
        self.allow_undefined = allow_undefined
        super(JSONNull, self).__init__(**kwargs)

    def validate(self, obj, value):
        if self.allow_undefined and value is undefined:
            return value
        elif value is None:
            return value
        self.error(obj, value)


class JSONNumber(T.Float):
    allow_undefined = True
    default_value = undefined
    info_text = "a JSON number"

    def __init__(self, allow_undefined=True, **kwargs):
        self.allow_undefined = allow_undefined
        super(JSONNumber, self).__init__(**kwargs)

    def validate(self, obj, value):
        if self.allow_undefined and value is undefined:
            return value
        return super(JSONNumber, self).validate(obj, value)


class JSONString(T.Unicode):
    allow_undefined = True
    default_value = undefined
    info_text = "a JSON string"

    def __init__(self, allow_undefined=True, **kwargs):
        self.allow_undefined = allow_undefined
        super(JSONString, self).__init__(**kwargs)

    def validate(self, obj, value):
        if self.allow_undefined and value is undefined:
            return value
        return super(JSONString, self).validate(obj, value)


class JSONBoolean(T.Bool):
    allow_undefined = True
    default_value = undefined
    info_text = "a JSON boolean"

    def __init__(self, allow_undefined=True, **kwargs):
        self.allow_undefined = allow_undefined
        super(JSONBoolean, self).__init__(**kwargs)

    def validate(self, obj, value):
        if self.allow_undefined and value is undefined:
            return value
        return super(JSONBoolean, self).validate(obj, value)

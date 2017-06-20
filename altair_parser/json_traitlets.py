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


class JSONInteger(T.Integer):
    allow_undefined = True
    default_value = undefined
    info_text = "a JSON integer"

    def __init__(self, allow_undefined=True, **kwargs):
        self.allow_undefined = allow_undefined
        super(JSONInteger, self).__init__(**kwargs)

    def validate(self, obj, value):
        if self.allow_undefined and value is undefined:
            return value
        return super(JSONInteger, self).validate(obj, value)


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


class JSONUnion(T.Union):
    allow_undefined = True
    default_value = undefined
    info_text = "a Union of types"

    def __init__(self, trait_types, allow_undefined=True, **kwargs):
        self.allow_undefined = allow_undefined
        super(JSONUnion, self).__init__(trait_types, **kwargs)

    def validate(self, obj, value):
        if self.allow_undefined and value is undefined:
            return value
        return super(JSONUnion, self).validate(obj, value)


class JSONArray(T.List):
    allow_undefined = True
    default_value = undefined
    info_text = "an Array of values"

    def __init__(self, trait, allow_undefined=True, **kwargs):
        self.allow_undefined = allow_undefined
        super(JSONArray, self).__init__(trait, **kwargs)

    def validate(self, obj, value):
        if self.allow_undefined and value is undefined:
            return value
        return super(JSONArray, self).validate(obj, value)


class JSONEnum(T.Enum):
    allow_undefined = True
    default_value = undefined
    info_text = "an enum of values"

    def __init__(self, values, allow_undefined=True, **kwargs):
        self.allow_undefined = allow_undefined
        super(JSONEnum, self).__init__(values, **kwargs)

    def validate(self, obj, value):
        if self.allow_undefined and value is undefined:
            return value
        return super(JSONEnum, self).validate(obj, value)


class JSONInstance(T.Instance):
    allow_undefined = True
    default_value = undefined
    info_text = "an instance of an object"

    def __init__(self, instance, allow_undefined=True, **kwargs):
        self.allow_undefined = allow_undefined
        super(JSONInstance, self).__init__(instance, **kwargs)

    def validate(self, obj, value):
        if self.allow_undefined and value is undefined:
            return value
        return super(JSONInstance, self).validate(obj, value)


class JSONAnyOf(T.Union):
    pass

class JSONOneOf(T.Union):
    # TODO: specialize validation code: must match exactly one example
    pass

class JSONAllOf(T.Union):
    # TODO: specialize validation code: must match all examples
    pass

class JSONNot(T.TraitType):
    allow_undefined = True
    default_value = undefined

    def __init__(self, not_this, allow_undefined=True, **kwargs):
        self.not_this = not_this
        self.allow_undefined = allow_undefined
        self.info_text = "not({0})".format(self.not_this.info_text)
        super(JSONNull, self).__init__(**kwargs)

    def validate(self, obj, value):
        if self.allow_undefined and value is undefined:
            return value
        try:
            self.not_this.validate(obj, value)
        except T.TraitError
            return True
        else:
            return False


# TODO: - create traits for OneOf(), Not()
#       - create meta-trait for multiple checks in one? Use Allof?

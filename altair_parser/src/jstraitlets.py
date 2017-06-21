"""
Extensions to traitlets for compatibility with JSON Schema
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
    allow_undefined = True
    default_value = undefined

    def __init__(self, trait_types, allow_undefined=True, **kwargs):
        self.allow_undefined = allow_undefined
        super(JSONAnyOf, self).__init__(trait_types, **kwargs)
        self.info_text = "AnyOf({0})".format(", ".join(tt.info() for tt in self.trait_types))

    def validate(self, obj, value):
        if self.allow_undefined and value is undefined:
            return value
        return super(JSONAnyOf, self).validate(obj, value)


class JSONOneOf(T.Union):
    allow_undefined = True
    default_value = undefined

    def __init__(self, trait_types, allow_undefined=True, **kwargs):
        self.allow_undefined = allow_undefined
        super(JSONOneOf, self).__init__(trait_types, **kwargs)
        self.info_text = "OneOf({0})".format(", ".join(tt.info() for tt in self.trait_types))

    def validate(self, obj, value):
        if self.allow_undefined and value is undefined:
            return value

        # Should validate against only one of the trait types
        valid_count = 0
        with obj.cross_validation_lock:
            for trait_type in self.trait_types:
                try:
                    v = trait_type._validate(obj, value)
                except T.TraitError:
                    continue
                valid_count += 1
            if valid_count == 1:
                # In the case of an element trait, the name is None
                if self.name is not None:
                    setattr(obj, '_' + self.name + '_metadata', trait_type.metadata)
                return v
        self.error(obj, value)


class JSONAllOf(T.Union):
    allow_undefined = True
    default_value = undefined

    def __init__(self, trait_types, allow_undefined=True, **kwargs):
        self.allow_undefined = allow_undefined
        super(JSONAllOf, self).__init__(trait_types, **kwargs)
        self.info_text = "AllOf({0})".format(", ".join(tt.info() for tt in self.trait_types))

    def validate(self, obj, value):
        if self.allow_undefined and value is undefined:
            return value

        # should validate against all of the trait types
        with obj.cross_validation_lock:
            for trait_type in self.trait_types:
                v = trait_type._validate(obj, value)
                # In the case of an element trait, the name is None
                if self.name is not None:
                    setattr(obj, '_' + self.name + '_metadata', trait_type.metadata)
                return v
        self.error(obj, value)


class JSONNot(T.TraitType):
    allow_undefined = True
    default_value = undefined

    def __init__(self, not_this, allow_undefined=True, **kwargs):
        self.not_this = not_this
        self.allow_undefined = allow_undefined
        self.info_text = "Not({0})".format(self.not_this.info())
        super(JSONNot, self).__init__(**kwargs)

    def validate(self, obj, value):
        if self.allow_undefined and value is undefined:
            return value
        try:
            self.not_this.validate(obj, value)
        except T.TraitError:
            return True
        else:
            self.error(obj, value)

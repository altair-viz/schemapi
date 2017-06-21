"""
Extensions to traitlets for compatibility with JSON Schema

The biggest difference between these trait types and the built-in trait types
is the addition of the ``undefined`` sentinel. Javascript has both a "null"
and an "undefined" marker, while Python uses "None" for both.
"""
import traitlets as T
from traitlets.traitlets import class_of


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
        kwargs['allow_none'] = True
        super(JSONNull, self).__init__(**kwargs)

    def validate(self, obj, value):
        if self.allow_undefined and value is undefined:
            return value
        elif value is None:
            return value
        else:
            self.error(obj, value)


def _validate_numeric(trait, obj, value,
                      minimum=undefined, maximum=undefined,
                      exclusiveMinimum=undefined, exclusiveMaximum=undefined,
                      multipleOf=undefined, **extra_kwds):
    if value is None:
        return value

    if minimum is not undefined:
        exclusive = exclusiveMinimum is not undefined and exclusiveMinimum
        if value < minimum or (exclusive and value == minimum):
            raise T.TraitError(
                "The value of the '{name}' trait of {klass} instance should "
                "not be less than {min_bound}, but a value of {value} was "
                "specified".format(
                    name=trait.name, klass=class_of(obj),
                    value=value, min_bound=minimum))

    if maximum is not undefined:
        exclusive = exclusiveMaximum is not undefined and exclusiveMaximum
        if value > maximum or (exclusive and value == maximum):
            raise T.TraitError(
                "The value of the '{name}' trait of {klass} instance should "
                "not be greater than {max_bound}, but a value of {value} was "
                "specified".format(
                    name=trait.name, klass=class_of(obj),
                    value=value, max_bound=maximum))

    if multipleOf is not undefined:
        if value % multipleOf != 0:
            raise T.TraitError(
                "The value of the '{name}' trait of {klass} instance should "
                "be a multiple of {multiple}, but a value of {value} was "
                "specified".format(
                    name=trait.name, klass=class_of(obj),
                    value=value, multiple=multipleOf))
    return value


class JSONNumber(T.Float):
    allow_undefined = True
    default_value = undefined
    info_text = "a JSON number"
    _validation_keywords = ["minimum", "maximum", "exclusiveMinimum",
                            "exclusiveMaximum", "multipleOf"]

    def __init__(self, allow_undefined=True, **kwargs):
        self.allow_undefined = allow_undefined
        self._validation_dict = {key: kwargs.pop(key)
                                 for key in self._validation_keywords
                                 if key in kwargs}
        super(JSONNumber, self).__init__(**kwargs)

    def validate(self, obj, value):
        if self.allow_undefined and value is undefined:
            return value
        value = super(JSONNumber, self).validate(obj, value)
        return _validate_numeric(self, obj, value, **self._validation_dict)


class JSONInteger(T.Integer):
    allow_undefined = True
    default_value = undefined
    info_text = "a JSON integer"
    _validation_keywords = ["minimum", "maximum", "exclusiveMinimum",
                            "exclusiveMaximum", "multipleOf"]

    def __init__(self, allow_undefined=True, **kwargs):
        self.allow_undefined = allow_undefined
        self._validation_dict = {key: kwargs.pop(key)
                                 for key in self._validation_keywords
                                 if key in kwargs}
        super(JSONInteger, self).__init__(**kwargs)

    def validate(self, obj, value):
        if self.allow_undefined and value is undefined:
            return value
        value = super(JSONInteger, self).validate(obj, value)
        return _validate_numeric(self, obj, value, **self._validation_dict)


class JSONString(T.Unicode):
    allow_undefined = True
    default_value = undefined
    info_text = "a JSON string"

    def __init__(self, allow_undefined=True, minLength=None, maxLength=None,
                 **kwargs):
        self.allow_undefined = allow_undefined
        self.minLength = minLength
        self.maxLength = maxLength
        super(JSONString, self).__init__(**kwargs)

    def _validate_string_length(self, obj, value):
        if self.minLength is not None and len(value) < self.minLength:
            raise T.TraitError(
                "The value of the '{name}' trait of {klass} instance should "
                "not be shorter than {minLength}, but a value of {value} was "
                "specified".format(
                    name=self.name, klass=class_of(obj),
                    value=value, minLength=self.minLength))

        if self.maxLength is not None and len(value) > self.maxLength:
            raise T.TraitError(
                "The value of the '{name}' trait of {klass} instance should "
                "not be longer than {maxLength}, but a value of {value} was "
                "specified".format(
                    name=self.name, klass=class_of(obj),
                    value=value, maxLength=self.maxLength))
        return value

    def validate(self, obj, value):
        if self.allow_undefined and value is undefined:
            return value
        value = super(JSONString, self).validate(obj, value)
        return self._validate_string_length(obj, value)


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
        if 'minItems' in kwargs:
            kwargs['minlen'] = kwargs.pop('minItems')
        if 'maxItems' in kwargs:
            kwargs['maxlen'] = kwargs.pop('maxItems')
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

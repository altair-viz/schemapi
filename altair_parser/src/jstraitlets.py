"""
Extensions to traitlets for compatibility with JSON Schema

The biggest difference between these trait types and the built-in trait types
is the addition of the ``undefined`` sentinel. Javascript has both a "null"
and an "undefined" marker, while Python uses "None" for both.

Additionally, these traits support validation keywords related to those
defined in the JSON Schema specification: http://json-schema.org.
The code here targets jsonschema draft 04.
"""
import copy

import traitlets as T
from traitlets.traitlets import class_of
from traitlets.utils.importstring import import_item
import six

__jsonschema_draft__ = 4


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


class JSONHasTraits(T.HasTraits):
    """A version of HasTraits with a few extra features:

    - supports default member types
    - supports to_dict() method and from_dict() class method

    Example
    -------
    >>> class Foo(JSONHasTraits):
    ...     _additional_traits = [T.Integer()]
    ...     name = T.Unicode()
    >>> f = Foo(name="Guido", score=42)
    >>> f.set_trait('value', 100)
    >>> f.trait_names()
    ['name', 'score', 'value']
    """
    _additional_traits = True

    def __init__(self, *args, **kwargs):
        default = self._get_additional_traits()
        if default:
            self.add_traits(**{key: default for key in kwargs
                               if key not in self.traits()})
        super(JSONHasTraits, self).__init__(*args, **kwargs)

    def _get_additional_traits(self):
        try:
            default = self._additional_traits[0]
        except TypeError:
            default = self._additional_traits

        if isinstance(default, T.TraitType):
            return default
        elif default:
            return T.Any()
        else:
            return None

    def set_trait(self, name, value):
        default = self._get_additional_traits()
        if default and name not in self.traits():
            self.add_traits(**{name: default})
        super(JSONHasTraits, self).set_trait(name, value)

    @classmethod
    def from_dict(cls, dct):
        """Initialize an instance from a (nested) dictionary"""
        # TODO: make this gracefully handle default values as well
        obj = cls()
        if not isinstance(dct, dict):
            raise T.TraitError("Argument to from_dict should be a dict, "
                               "but got {0}".format(dct))
        for key, val in dct.items():
            if isinstance(val, dict):
                trait = obj.traits()[key]
                subtraits = trait.trait_types if isinstance(trait, T.Union) else [trait]
                for subtrait in subtraits:
                    if isinstance(subtrait, T.Instance) and issubclass(subtrait.klass, JSONHasTraits):
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
            if isinstance(val, JSONHasTraits):
                val = val.to_dict()
            dct[key] = val
        return dct


class HasTraitsUnion(JSONHasTraits):
    """A HasTraits class built from a union of other HasTraits objects"""
    _classes = []
    def __init__(self, *args, **kwargs):
        for cls in self._classes:
            if isinstance(cls, six.string_types):
                cls = import_item(cls)
            if all(key in cls.class_traits() for key in kwargs):
                try:
                    cls(*args, **kwargs)
                except (T.TraitError, ValueError):
                    pass
                else:
                    self.add_traits(**{key: copy.copy(val) for key, val
                                       in cls.class_traits().items()})
                    break
        else:
            raise T.TraitError("{cls}: initialization arguments not "
                               "valid in any wrapped classes"
                               "".format(cls=self.__class__.__name__))
        super(HasTraitsUnion, self).__init__(*args, **kwargs)

    @classmethod
    def from_dict(cls, dct):
        for subcls in cls._classes:
            if isinstance(subcls, six.string_types):
                subcls = import_item(subcls)
            if all(key in subcls.class_traits() for key in dct):
                try:
                    obj = subcls.from_dict(dct)
                except (T.TraitError, ValueError):
                    pass
                else:
                    return cls(**{name: getattr(obj, name)
                                  for name in obj.trait_names()})
        else:
            raise T.TraitError("{cls}: dict representation not "
                               "valid in any wrapped classes"
                               "".format(cls=cls.__name__))


def AnonymousMapping(**traits):
    """Create an anonymous HasTraits mapping

    This is used when a JSONSchema defines an object inline, rather than in
    a separate statement

    Example
    -------
    >>> Foo = AnonymousMapping(val=T.Integer())
    >>> f = Foo(val=4)
    >>> type(f)
    <class 'traitlets.traitlets.AnonymousMapping'>
    """
    return T.MetaHasTraits('AnonymousMapping', (JSONHasTraits,), traits)


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


def _has_unique_elements(L):
    """Return True if all items in the list are unique"""
    # Hashable types
    try:
        S = set(L)
    except TypeError:
        pass
    else:
        return len(L) == len(S)

    # Unhashable but orderable types
    try:
        L = sorted(L)
    except TypeError:
        pass
    else:
        from itertools import groupby
        return len(L) == len([k for k, v in groupby(L)])

    # Unhashable, unorderable types
    return all(L[i] != L[j]
               for i in range(len(L))
               for j in range(i + 1, len(L)))


class JSONArray(T.List):
    allow_undefined = True
    default_value = undefined
    info_text = "an Array of values"

    def __init__(self, trait, allow_undefined=True, uniqueItems=False, **kwargs):
        self.allow_undefined = allow_undefined
        self.uniqueItems = uniqueItems
        if 'minItems' in kwargs:
            kwargs['minlen'] = kwargs.pop('minItems')
        if 'maxItems' in kwargs:
            kwargs['maxlen'] = kwargs.pop('maxItems')
        super(JSONArray, self).__init__(trait, **kwargs)

    def validate(self, obj, value):
        if self.allow_undefined and value is undefined:
            return value
        value = super(JSONArray, self).validate(obj, value)
        if self.uniqueItems and not _has_unique_elements(value):
            raise T.TraitError(
                "The value of the '{name}' trait of {klass} instance should "
                "have unique elements".format(
                    name=self.name, klass=class_of(obj)))
        return value


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

    def make_dynamic_default(self):
        if self.allow_undefined:
            return undefined
        else:
            return super(JSONInstance, self).make_dynamic_default()

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
            return value
        else:
            self.error(obj, value)

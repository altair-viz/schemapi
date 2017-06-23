import re
import keyword

def hash_schema(schema, hashfunc=hash):
    """Compute a unique hash for a (nested) schema

    Unlike the built-in hash() function, this handles
    dicts, lists, and sets in addition to tuples.
    """
    def make_hashable(val):
        if isinstance(val, list):
            return tuple(make_hashable(v) for v in val)
        elif isinstance(val, set):
            return frozenset(make_hashable(v) for v in val)
        elif isinstance(val, dict):
            return frozenset((k, make_hashable(v)) for k, v in val.items())
        else:
            return val
    return hashfunc(make_hashable(schema))


def regularize_name(name):
    """Regaularize a string to be a valid Python identifier

    Examples
    --------
    >>> regularize_name("classname<(string|int)>")
    'classname_string_int_'
    >>> regularize_name("foo.bar")
    'foo_bar'
    >>> regularize_name("9abc")
    '_9abc'
    """
    name, subs = re.subn('[^_a-zA-Z0-9]+', '_', name)
    if name[0].isdigit():
        name = '_' + name
    if keyword.iskeyword(name):
        name = '_' + name
    return name

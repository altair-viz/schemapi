import re
import keyword
import textwrap


def sorted_repr(obj):
    """return repr(obj), but if obj is a dict then ensure keys are sorted"""
    if isinstance(obj, dict):
        try:
            items = sorted(obj.items())
        except TypeError: # items cannot be sorted
            items = obj.items()
        return '{{{0}}}'.format(', '.join(repr(key) + ': ' + sorted_repr(val)
                                          for key, val in items))
    else:
        return repr(obj)


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


def regularize_name(name, duplicates=[]):
    """Regaularize a string to be a valid Python identifier

    Optionally, ``duplicates`` can be provided and the resulting name will
    be assured to avoid dublicates

    Examples
    --------
    >>> regularize_name("classname<(string|int)>")
    'classname_string_int'
    >>> regularize_name("foo.bar")
    'foo_bar'
    >>> regularize_name("9abc")
    '_9abc'
    """

    is_identifier = lambda s: (re.match("^[_A-Za-z][_a-zA-Z0-9]*$", s)
                               and not keyword.iskeyword(s))

    if not is_identifier(name):
        # replace all non alphanumeric characters with an underscore
        name, subs = re.subn('[^_a-zA-Z0-9]+', '_', name)

        # strip leading and trailing underscores
        name = name.strip('_')

        # if the first character is a digit, use a leading underscore
        if name[0].isdigit():
            name = '_{0}'.format(name)

        # if the result is a reserved Python keyword, add a trailing underscore
        if keyword.iskeyword(name):
            name = '{0}_'.format(name)

    # if the result is among duplicates, add an integer at the end
    base_count = re.compile('^([_A-Za-z0-9]+?)([0-9]*)$')
    if name in duplicates:
        base, count = base_count.match(name).groups()
        count = int(count) if count else 0
        while name in duplicates:
            count += 1
            name = "{0}{1}".format(base, count)
    return name


def trait_name_map(names):
    """Build a mapping of regularized names to input names

    Names which require no modification are excluded from the mapping
    """
    mapping = {}
    for name in names:
        duplicates = (set(names) - {name}) | set(mapping.keys())
        reg_name = regularize_name(name, duplicates)
        if name != reg_name:
            mapping[reg_name] = name
    return mapping


def format_description(content, width=70, indent=8, indent_first=False):
    """Format documentation description"""
    # TODO: document, test, and use
    lines = content.splitlines()

    def format_line(line):
        if line.startswith('-'):
            return textwrap.indent(textwrap.fill(line, width - indent - 2),
                                   (indent + 2) * ' ')[2:]
        else:
            return textwrap.indent(textwrap.fill(line, width - indent),
                                   indent * ' ')

    result = '\n'.join(format_line(line) for line in lines if line)
    if not indent_first:
        result = result.lstrip()
    return result

import re
import keyword
import textwrap


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
    'classname_string_int'
    >>> regularize_name("foo.bar")
    'foo_bar'
    >>> regularize_name("9abc")
    '_9abc'
    """
    if name == '$schema':
        return 'schema'
    elif name == '$id':
        return 'id'
    name, subs = re.subn('[^_a-zA-Z0-9]+', '_', name)
    name = name.strip('_')
    if name[0].isdigit():
        name = '_' + name
    if keyword.iskeyword(name):
        name = name + '_'
    return name


def format_description(content, width=70, indent=8, indent_first=False):
    """Format documentation description"""
    # TODO: document, test, and use
    lines = content.splitlines()
    def format_line(line):
        if line.startswith('-'):
            return textwrap.indent(textwrap.fill(line, width - indent - 2),
                                   (indent + 2) * ' ')[2:]
        else:
            return textwrap.indent(textwrap.fill(line, width - indent), indent * ' ')
    result = '\n'.join(format_line(line) for line in lines if line)
    if not indent_first:
        result = result.lstrip()
    return result

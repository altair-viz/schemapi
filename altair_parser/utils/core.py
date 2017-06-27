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

def make_ascii_compatible(s):
    """Ensure a string is ascii-compatible.
    This is not an issue for Python 3, but if used in code will break Python 2
    """
    # Replace common non-ascii characters with suitable equivalents
    s = s.replace('\u2013', '-')
    s.encode('ascii')  # if this errors, then add more replacements above
    return s


def format_description(content, width=70, indent=8, indent_first=False):
    """Format documentation description"""
    # TODO: document, test, and use
    lines = content.splitlines()
    def format_line(line):
        line = line.replace("__Default value:__", "Default:")
        if line.startswith('-'):
            return textwrap.indent(textwrap.fill(line, width - indent - 2),
                                   (indent + 2) * ' ')[2:]
        else:
            return textwrap.indent(textwrap.fill(line, width - indent), indent * ' ')
    result = '\n'.join(format_line(line) for line in lines if line)
    if not indent_first:
        result = result.lstrip()
    return result

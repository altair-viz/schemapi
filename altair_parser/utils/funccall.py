"""Utilities for constructing function calls"""

class Variable(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return str(self.name)


def construct_function_call(funcname, *args, **kwargs):
    """Construct a string version of a Python function call

    The repr() of args and kwargs will be used.

    Examples
    --------
    >>> construct_function_call("func")
    'func()'
    >>> construct_function_call("add", 4, 5)
    'add(4, 5)'
    >>> construct_function_call("foo", Variable('bar'), default=True)
    'foo(bar, default=True)'
    """
    args = ', '.join(repr(arg) for arg in args)
    if args and kwargs:
        args += ', '
    kwargs = ', '.join(key + '=' + repr(val)
                       for key, val in sorted(kwargs.items()))
    return "{funcname}({args}{kwargs})".format(funcname=funcname,
                                               args=args,
                                               kwargs=kwargs)

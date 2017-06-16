"""Tools for dynamically importing generated modules from memory"""

# TODO: this works in Python 3.6... need to test in older Python versions

import sys
import os
from types import ModuleType

spec = {
    'package': 'dynmod',
    'contents': {
        '__init__.py': {
            'code': ('from .foo import x\n'
                     'from .bar import y\n'),
            'dependencies': ['foo', 'bar']
        },
        'foo.py': {
            'code': 'x = 10',
        },
        'bar.py': {
            'code': ('from .foo import x\n'
                     'y = 4 * x'),
            'dependencies': ['foo']
        },
    },
    'subpackages': [
        {
            'package': 'utils',
            'contents': {
                '__init__.py': {
                    'code': 'pi = 3.1415'
                }
            }
        }
    ],
}


def load_dynamic_module(spec, parent=''):
    """Load a dynamically imported module

    Parameters
    ----------
    spec : dict
        A dictionary specifying the module to load
    parent : string (optional)
        The name of the parent module, if any

    Returns
    -------
    mod : ModuleType
        The dynamically loaded module

    Notes
    -----
    spec should be a dict with up to three keys:
    - 'package' (required): a string giving the name of the package
    - 'contents' (optional): a dict mapping filenames to filespecs (see below)
    - 'subpackages' (optional): a list of module specs

    filespecs should be a dict with up to two keys:
    - 'code': a string giving the content of the file
    - 'dependencies': a list of modules the code imports

    Examples
    --------
    >>> spec = {'package': 'mymod',
    ...         'contents': {'__init__.py': {'code': 'x = 4'},
    ...                      'foo.py': {'code': 'message="hello world"'}}}
    >>> mymod = load_dynamic_module(spec)
    >>> mymod.x
    4
    >>> from mymod.foo import message
    >>> print(message)
    hello world
    """
    # TODO: actually build a dependency graph
    # TODO: handle dependencies between packages?

    expected_keys = {'package', 'subpackages', 'contents'}
    unrecognized_keys = set(spec.keys()) - expected_keys
    if unrecognized_keys:
        raise ValueError("unrecognized keys: " + str(unrecognized_keys))
    if parent:
        packagename = parent + '.' + spec['package']
    else:
        packagename = spec['package']
    sys.modules[packagename] = ModuleType(packagename)

    for subpackage in spec.get('subpackages', []):
        load_dynamic_module(subpackage, parent=packagename)

    # Maintain a queue to make sure dependencies are loaded in the correct order
    # TODO: correctly handle circular imports?
    queue = list(spec.get('contents', {}).keys())
    loaded = set()

    # seeking_dep is what we use to make sure circular imports don't result in
    # infinite loops. Building a dependency graph would be a better approach
    seeking_dep = None

    while queue:
        filename = queue.pop(0)
        contents = spec['contents'][filename]
        code = contents.get('code', '')
        deps = set(contents.get('dependencies', []))
        root, ext = os.path.splitext(filename)
        assert ext == '.py'

        # if dependencies are not loaded, then don't execute this now
        if loaded.intersection(deps) < deps:
            queue.append(filename)
            if seeking_dep == filename:
                raise ValueError("circular import detected")
            if seeking_dep is None:
                seeking_dep = filename
            continue

        if code:
            if filename == '__init__.py':
                exec(code, sys.modules[packagename].__dict__)
            else:
                modulename = packagename + '.' + root
                sys.modules[modulename] = ModuleType(modulename)
                exec(code, sys.modules[modulename].__dict__)

        loaded.add(root)

        # No longer seeking a dependency
        seeking_dep = None

    return sys.modules[packagename]

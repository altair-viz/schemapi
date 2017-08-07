"""Tools for dynamically importing generated modules from memory"""

# TODO: this works in Python 3.6... need to test in older Python versions
# TODO: define the JSON schema for the specifications below

import sys
import types
import importlib
import importlib.abc


class DynamicImporter(importlib.abc.MetaPathFinder):
    """An import hook for dynamic imports

    This class is a finder and loader in one.
    """
    def __init__(self, **pkgspecs):
        self.pkgspecs = pkgspecs

    def update(self, **pkgspecs):
        self.pkgspecs.update(pkgspecs)

    def _get_spec(self, fullname):
        names = fullname.split('.')
        context = self.pkgspecs
        for name in names[:-1]:
            context = context[name]
        return names[-1], context

    def _in_package(self, fullname):
        try:
            name, spec = self._get_spec(fullname)
        except KeyError:
            return False
        else:
            return (name in spec) or (name + '.py' in spec)

    def _is_package(self, fullname):
        name, spec = self._get_spec(fullname)
        if name in spec:
            return True
        elif name + '.py' in spec:
            return False

    def _get_code(self, fullname):
        name, spec = self._get_spec(fullname)
        if name in spec:
            return spec[name].get('__init__.py', '')
        elif name + '.py' in spec:
            return spec[name + '.py']
        else:
            raise KeyError()

    def find_module(self, fullname, path=None):
        if self._in_package(fullname):
            return self
        else:
            return None

    def load_module(self, fullname):
        # Following PEP 302
        code = self._get_code(fullname)
        ispkg = self._is_package(fullname)

        module = sys.modules.setdefault(fullname, types.ModuleType(fullname))
        module.__name__ = fullname
        module.__file__ = "<{0}>".format(self.__class__.__name__)
        module.__loader__ = self
        if ispkg:
            module.__path__ = []
            module.__package__ = fullname
        else:
            module.__package__ = fullname.rpartition('.')[0]
        if code:
            exec(code, module.__dict__)
        return module


def load_dynamic_module(name, specification, reload_module=False):
    """Dynamically import and load a module defined via a dict specification

    Parameters
    ----------
    name : string
        The name of the module to create and load
    specification : dict
        A dictionary specifying the content of the module (see below)
    reload_module : boolean
        If True, then remove any previous version of the package

    Returns
    -------
    mod : ModuleType
        The dynamically loaded module

    Examples
    --------
    >>> spec = {'__init__.py': 'from .foo import message',
    ...         'foo.py': 'message="hello world"',
    ...         'utils': {'__init__.py': 'f = lambda x: 2 * x'}}
    >>> mymod = load_dynamic_module('mymod', spec)
    >>> print(mymod.message)
    hello world
    >>> from mymod.utils import f
    >>> f(10)
    20
    """
    dct = {name: specification}
    if isinstance(sys.meta_path[0], DynamicImporter):
        sys.meta_path[0].update(**dct)
    else:
        importer = DynamicImporter(**dct)
        sys.meta_path.insert(0, importer)
    if reload_module and name in sys.modules:
        for pkgname in list(sys.modules.keys()):
            if pkgname.split('.')[0] == name:
                del sys.modules[pkgname]
    return importlib.import_module(name)

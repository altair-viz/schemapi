"""Tools for dynamically importing generated modules from memory"""

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
            seeking_dep = seeking_dep or filename
            continue
            
        if code:
            if filename == '__init__.py':
                exec(code, sys.modules[packagename].__dict__)
            else:
                modulename = packagename + '.' + root
                sys.modules[modulename] = ModuleType(modulename)
                exec(code, sys.modules[modulename].__dict__)
        loaded.add(root)
        seeking_dep = None
        
    return sys.modules[packagename]
        
dynmod = load_dynamic_module(spec)
print(dynmod.x, dynmod.y)
from dynmod import utils
utils.pi

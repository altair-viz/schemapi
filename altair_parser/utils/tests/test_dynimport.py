import pytest

from .. import load_dynamic_module

SPEC = {
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


def test_dynamic_module():
    dynmod = load_dynamic_module(SPEC)
    from dynmod import utils
    assert dynmod.x == 10
    assert dynmod.y == 40
    assert utils.pi == 3.1415

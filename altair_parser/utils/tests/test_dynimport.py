from .. import load_dynamic_module

dynmod_spec = {
    '__init__.py': ('from .foo import x\n'
                    'from .bar import y\n'),
    'foo.py': 'x = 10',
    'bar.py': ('from .foo import x\n'
               'y = 4 * x'),
    'utils': {
                '__init__.py': 'pi = 3.1415'
             }
}


def test_dynamic_module():
    dynmod = load_dynamic_module('dynmod', dynmod_spec)
    from dynmod import utils
    assert dynmod.x == 10
    assert dynmod.y == 40
    assert utils.pi == 3.1415

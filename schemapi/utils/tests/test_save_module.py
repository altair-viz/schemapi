import sys
import tempfile
import contextlib

import pytest

from .. import save_module


@pytest.fixture
def spec():
    return {
            '__init__.py': "from .hypot import hypotenuse",
            'hypot.py': ("from .utils import square\n"
                         "from math import sqrt\n"
                         "hypotenuse = lambda a, b: sqrt(square(a) + square(b))"),
            'utils': {
                '__init__.py': 'square = lambda x: x ** 2'
            }
           }


@contextlib.contextmanager
def temporary_import(module):
    """Context manager to temporarily import a module and remove it afterward"""
    assert module not in sys.modules
    yield
    sys.modules = {name: mod for name, mod in sys.modules.items()
                   if name.split('.', 1)[0] != module}


@contextlib.contextmanager
def import_path(*paths):
    """Context manager to set temporary import paths"""
    old_paths = sys.path
    sys.path = list(paths)
    yield
    sys.path = old_paths


def test_save_module(spec):
    modname = '_tmp_mod'
    with tempfile.TemporaryDirectory() as tmpdir:
        save_module(spec, name=modname, location=tmpdir)
        with import_path(tmpdir):
            with temporary_import(modname):
                from _tmp_mod import hypotenuse
                assert hypotenuse(3, 4) == 5

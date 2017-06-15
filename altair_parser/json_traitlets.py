"""
Extensions to traitlets for use with JSON
"""

# Do this so that we can import this module in place of traitlets
from traitlets import *

import traitlets as T


class Null(TraitType):
    """A trait for complex numbers."""

    default_value = None
    info_text = 'a null value'

    def validate(self, obj, value):
        if value is None:
            return value
        self.error(obj, value)

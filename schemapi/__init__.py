"""
schemapi: tools for generating Python APIs from JSON schemas
"""
from .schemapi import SchemaBase, Undefined
from .decorator import schemaclass
from .utils import SchemaInfo
from .codegen import module_code, write_module
from .version import version, full_version

__version__ = version


__all__ = (
    "SchemaBase",
    "Undefined",
    "schemaclass",
    "SchemaInfo",
    "module_code",
    "write_module"
)

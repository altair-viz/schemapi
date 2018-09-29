"""Code generation utilities"""
from .utils import SchemaInfo, is_valid_identifier, indent_docstring, indent_arglist

import os
import pprint
import re
import textwrap


import pkgutil
import json


def load_metaschema():
    """Load the json schema associated with this module's functions"""
    return json.loads(pkgutil.get_data(__name__, 'jsonschema-draft04.json').decode('utf-8'))


class CodeSnippet(object):
    """Object whose repr() is a string of code"""
    def __init__(self, code):
        self.code = code

    def __repr__(self):
        return self.code


def _get_args(info):
    """Return the list of args & kwds for building the __init__ function"""
    # TODO: - set additional properties correctly
    #       - handle patternProperties etc.
    required = set()
    kwds = set()
    invalid_kwds = set()

    # TODO: specialize for anyOf/oneOf?

    if info.is_allOf():
        # recursively call function on all children
        arginfo = [_get_args(child) for child in info.allOf]
        nonkeyword = all(args[0] for args in arginfo)
        required = set.union(set(), *(args[1] for args in arginfo))
        kwds = set.union(set(), *(args[2] for args in arginfo))
        invalid_kwds = set.union(set(), *(args[3] for args in arginfo))
        additional = all(args[4] for args in arginfo)
    elif info.is_empty() or info.is_compound():
        nonkeyword = True
        additional = True
    elif info.is_value():
        nonkeyword = True
        additional=False
    elif info.is_object():
        invalid_kwds = ({p for p in info.required if not is_valid_identifier(p)} |
                        {p for p in info.properties if not is_valid_identifier(p)})
        required = {p for p in info.required if is_valid_identifier(p)}
        kwds = {p for p in info.properties if is_valid_identifier(p)}
        kwds -= required
        nonkeyword = False
        additional = True
        #additional = info.additionalProperties or info.patternProperties
    else:
        raise ValueError("Schema object not understood")

    return (nonkeyword, required, kwds, invalid_kwds, additional)


class SchemaGenerator(object):
    """Class that defines methods for generating code from schemas

    Parameters
    ----------
    classname : string
        The name of the class to generate
    schema : dict
        The dictionary defining the schema class
    rootschema : dict (optional)
        The root schema for the class
    basename : string (default: "SchemaBase")
        The name of the base class to use in the class definition
    schemarepr : CodeSnippet or object, optional
        An object whose repr will be used in the place of the explicit schema.
        This can be useful, for example, when the generated code should reference
        a predefined schema object. The user must ensure that the schema within
        the evaluated code is identical to the schema used to generate the code.
    rootschemarepr : CodeSnippet or object, optional
        An object whose repr will be used in the place of the explicit root
        schema.
    """
    schema_class_template = textwrap.dedent('''
    class {classname}({basename}):
        """{docstring}"""
        _schema = {schema!r}
        _rootschema = {rootschema!r}

        {init_code}
    ''')

    init_template = textwrap.dedent("""
    def __init__({arglist}):
        super({classname}, self).__init__({super_arglist})
    """).lstrip()

    def _process_description(self, description):
        return description

    def __init__(self, classname, schema, rootschema=None,
                 basename='SchemaBase', schemarepr=None, rootschemarepr=None,
                 nodefault=()):
        self.classname = classname
        self.schema = schema
        self.rootschema = rootschema
        self.basename = basename
        self.schemarepr = schemarepr
        self.rootschemarepr = rootschemarepr
        self.nodefault = nodefault

    def schema_class(self):
        """Generate code for a schema class"""
        rootschema = self.rootschema if self.rootschema is not None else self.schema
        schemarepr = self.schemarepr if self.schemarepr is not None else self.schema
        rootschemarepr = self.rootschemarepr
        if rootschemarepr is None:
            if rootschema is self.schema:
                rootschemarepr = CodeSnippet('_schema')
            else:
                rootschemarepr = rootschema
        return self.schema_class_template.format(
            classname=self.classname,
            basename=self.basename,
            schema=schemarepr,
            rootschema=rootschemarepr,
            docstring=self.docstring(indent=4),
            init_code=self.init_code(indent=4)
        )

    def docstring(self, indent=0):
        # TODO: add a general description at the top, derived from the schema.
        #       for example, a non-object definition should list valid type, enum
        #       values, etc.
        # TODO: use _get_args here for more information on allOf objects
        info = SchemaInfo(self.schema, self.rootschema)
        doc = ["{} schema wrapper".format(self.classname),
               '',
               info.medium_description]
        if info.description:
            doc += self._process_description( #remove condition description
                re.sub(r"\n\{\n(\n|.)*\n\}",'',info.description)).splitlines()

        if info.properties:
            nonkeyword, required, kwds, invalid_kwds, additional = _get_args(info)
            doc += ['',
                    'Attributes',
                    '----------',
                    '']
            for prop in sorted(required) + sorted(kwds) + sorted(invalid_kwds):
                propinfo = info.properties[prop]
                doc += ["{} : {}".format(prop, propinfo.short_description),
                        "    {}".format(self._process_description(propinfo.description))]
        if len(doc) > 1:
            doc += ['']
        return indent_docstring(doc, indent_level=indent, width=100, lstrip=True)

    def init_code(self, indent=0):
        """Return code suitablde for the __init__ function of a Schema class"""
        info = SchemaInfo(self.schema, rootschema=self.rootschema)
        nonkeyword, required, kwds, invalid_kwds, additional =_get_args(info)

        nodefault=set(self.nodefault)
        required -= nodefault
        kwds -= nodefault

        args = ['self']
        super_args = []

        if nodefault:
            args.extend(sorted(nodefault))
        elif nonkeyword:
            args.append('*args')
            super_args.append('*args')

        args.extend('{}=Undefined'.format(p)
                    for p in sorted(required) + sorted(kwds))
        super_args.extend('{0}={0}'.format(p)
                          for p in sorted(nodefault) + sorted(required) + sorted(kwds))

        if additional:
            args.append('**kwds')
            super_args.append('**kwds')

        arg_indent_level = 9 + indent
        super_arg_indent_level = 23 + len(self.classname) + indent

        initfunc = self.init_template.format(classname=self.classname,
                                             arglist=indent_arglist(args, indent_level=arg_indent_level),
                                             super_arglist=indent_arglist(super_args, indent_level=super_arg_indent_level))
        if indent:
            initfunc = ('\n' + indent * ' ').join(initfunc.splitlines())
        return initfunc

def module_code(schema, root_name='Root', schemapi_import='schemapi'):
    """Generate a Python module implementing the schema

    Parameters
    ----------
    schema : dict
        The root schema description
    root_name : string
        The name of the root class (default: 'Root')
    schemapi_import : string
        The import path for schemapi (default: 'schemapi')
    """
    import jsonschema
    metaschema = load_metaschema()
    jsonschema.validate(metaschema, schema)
    
    definitions = schema.get('definitions', {})

    if root_name in definitions:
        raise ValueError(f"root_name='{root_name}' exists in definitions; "
                        "please choose a different name")

    code = f"from {schemapi_import} import SchemaBase, Undefined\n\n"
    schemarepr = textwrap.indent(pprint.pformat(schema), 4 * ' ').lstrip()

    root = SchemaGenerator(root_name, schema,
                           schemarepr=CodeSnippet(schemarepr))
    code += root.schema_class() + '\n\n'
    
    for name, subschema in definitions.items():
        gen = SchemaGenerator(classname=name,
                            schema=subschema,
                            rootschema=schema,
                            schemarepr=CodeSnippet(f"{{'$ref': '#/definitions/{name}'}}"),
                            rootschemarepr=CodeSnippet(f'{root_name}._schema'))
        code += gen.schema_class() + '\n\n'
    return code


def write_module(schema, filename, root_name='Root', schemapi_import='schemapi'):
    code = module_code(schema, root_name=root_name, schemapi_import=schemapi_import)
    with open(filename, 'w') as f:
        f.write(code)
    return os.path.abspath(filename)

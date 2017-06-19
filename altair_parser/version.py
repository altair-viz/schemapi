from __future__ import absolute_import, division, print_function
import os

# Format expected by setup.py and doc/source/conf.py: string of form "X.Y.Z"
_version_major = 0
_version_minor = 1
_version_micro = ''  # use '' for first of series, number for 1 and above
_version_extra = 'dev'
# _version_extra = ''  # Uncomment this for full releases

# Construct full version string from these.
_ver = [_version_major, _version_minor]
if _version_micro:
    _ver.append(_version_micro)
if _version_extra:
    _ver.append(_version_extra)

__version__ = '.'.join(map(str, _ver))

CLASSIFIERS = ["Development Status :: 3 - Alpha",
               "Environment :: Console",
               "Intended Audience :: Science/Research",
               "License :: OSI Approved :: BSD License",
               "Operating System :: OS Independent",
               "Programming Language :: Python :: 3.6",
               "Topic :: Scientific/Engineering"]

# Description should be a one-liner:
description = "altair_parser: generate traitlets code from JSONSchema"
# Long description will go up on the pypi page
long_description = """
Altair-Parser
=============
Altair-Parser provides tools for auto-generation of traitlets object
hierarchies generated from JSONSchema definitions.
See more information in the README_.

.. _README: https://github.com/altair-viz/altair_parser/blob/master/README.md
"""

NAME = "altair_parser"
MAINTAINER = "Jake VanderPlas"
MAINTAINER_EMAIL = "jakevdp@uw.edu"
DESCRIPTION = description
LONG_DESCRIPTION = long_description
URL = "http://github.com/altair-viz/altair_parser"
DOWNLOAD_URL = ""
LICENSE = "BSD"
AUTHOR = "Jake VanderPlas"
AUTHOR_EMAIL = "jakevdp@uw.edu"
PLATFORMS = "OS Independent"
MAJOR = _version_major
MINOR = _version_minor
MICRO = _version_micro
VERSION = __version__
PACKAGE_DATA = {'altair_parser': [os.path.join('schemas', '*.json')]}
REQUIRES = ["jsonschema", "traitlets", "jinja2"]

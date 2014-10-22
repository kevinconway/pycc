"""Compatibility helpers for Py2 and Py3."""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import sys


PY2 = sys.version_info.major == 2
PY3 = not PY2

# Provide a nice range function for py2.
try:
    range = xrange
except NameError:
    pass

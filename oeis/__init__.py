# -*- coding: utf-8 -*- #
#
# oeis/__init__.py
#
#
# MIT License
#
# Copyright (c) 2019 Brandon Gomes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

"""
Interface to the OEIS.

"""

# -------------- Standard Library -------------- #

import sys

# ---------------- oeis Library ---------------- #

from ._version import __version_info__, __version__

from . import generators
from .core import *


A = SequenceFactory()
OEIS = Registry(sequence_factory=A)


PYTHON_37_GETATTR_IMPORT = sys.version_info.major == 3 and sys.version_info.minor == 7


__all__ = core.__all__ + ('A', 'OEIS', 'PYTHON_37_GETATTR_IMPORT')


def _module_getattr_wrapper(a, o):
    """"""
    def inner(name):
        if name == '__all__':
            return __all__
        try:
            return a.__call__(name)
        except Exception:  # TODO: except ?
            try:
                return getattr(o, name)
            except Exception:  # TODO: except ?
                pass
        raise ImportError("cannot import name '{name}' from 'oeis' ({path})".format(name=name, path=__file__))
    return inner


if PYTHON_37_GETATTR_IMPORT:
    __getattr__ = _module_getattr_wrapper(A, OEIS)


for g in map(lambda g: getattr(generators, g), generators.__all__):
    name = g.__name__
    if name.startswith('g'):
        OEIS.register(name.strip('g'), g, meta=True)

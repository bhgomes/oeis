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
from .sequence import *
from .util import value_or


GETATTR_IMPORT = sys.version_info >= (3, 7)


def _module_getattr_(a_, oeis_, file):
    """Customize Module Import Mechanism."""
    def inner(name):
        if name == '__all__':
            return __all__
        try:
            return a_.__call__(name)
        except Exception:  # TODO: except ?
            try:
                return getattr(oeis_, name)
            except Exception:  # TODO: except ?
                pass
        raise ImportError("cannot import name '{name}' from 'oeis' ({path})".format(name=name, path=file))
    return inner


def setup_module(generator_list, file, *, a_=None, oeis_=None):
    """Register all Included Generators."""
    a_ = value_or(a_, SequenceFactory(always_cache=True))
    oeis_ = value_or(oeis_, Registry.from_factory(a_))

    for generator in map(lambda g: getattr(generators, g), generator_list):
        name = generator.__name__
        if name.startswith('g'):
            oeis_.register(name.strip('g'), generator, meta=True)

    if GETATTR_IMPORT:
        return a_, oeis_, _module_getattr_(a_, oeis_, file)
    return a_, oeis_, lambda n: None


A, OEIS, __getattr__ = setup_module(generators.__all__, __file__)


__all__ = core.__all__ + ('A', 'OEIS', 'GETATTR_IMPORT')

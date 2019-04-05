# -*- coding: utf-8 -*- #
#
# tests/test_magic_import.py
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
Test Magic Import System.

"""

# -------------- Standard Library -------------- #

import sys

# -------------- External Library -------------- #

import pytest

# ---------------- oeis Library ---------------- #

import oeis
from .core import parametrized_ids


HAS_MAGIC_IMPORT = oeis.GETATTR_IMPORT


def test_version():
    assert (sys.version_info >= (3, 7)) == HAS_MAGIC_IMPORT


@parametrized_ids("number", 100)
@pytest.mark.skipif(
    not HAS_MAGIC_IMPORT, reason="Magic import only supported in Python 3.7+"
)
def test_magic_import(number):
    try:
        entry = getattr(oeis, "A" + str(number))
    except ImportError:
        pytest.skip("OEIS Entry {number} does not exist.".format(number=number))
    default_request = oeis.A(number)
    assert entry in oeis.OEIS
    assert default_request in oeis.OEIS
    assert entry == default_request

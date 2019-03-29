# -*- coding: utf-8 -*- #
#
# oeis/base.py
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

import re

# ---------------- oeis Library ---------------- #

from .util import is_int


__all__ = ("InvalidID", "name", "number", "OEIS_ID_REGEX", "find_references")


class InvalidID(KeyError):
    """
    Invalid OEIS ID.

    """

    @classmethod
    def from_key(cls, key):
        """Build Exception from Key."""
        return cls("Key {} must be a valid OEIS id.".format(key))


def _convert_string(key):
    """Convert OEIS String to Integer."""
    if isinstance(key, str):
        key = int(key.strip().upper().strip("A"))
    return key


def name(key):
    """Get Full Name for OEIS Sequence."""
    try:
        return key.__oeis_name__
    except AttributeError:
        pass
    key = _convert_string(key)
    if is_int(key):
        return "A{key:06d}".format(key=key)
    raise InvalidID.from_key(key)


def number(key):
    """Get Index of OEIS Sequence."""
    try:
        return key.__oeis_number__
    except AttributeError:
        pass
    key = _convert_string(key)
    if is_int(key):
        return key
    raise InvalidID.from_key(key)


OEIS_ID_REGEX = re.compile(r"(A\d+)", re.MULTILINE | re.UNICODE)


def find_references(text):
    """Find references to OEIS Sequences."""
    for match in re.finditer(OEIS_ID_REGEX, text):
        yield match.groups()

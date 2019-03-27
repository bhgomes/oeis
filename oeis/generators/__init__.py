# -*- coding: utf-8 -*- #
#
# oeis/generators/__init__.py
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

import itertools

# ---------------- oeis Library ---------------- #


__all__ = (
    'g27',
    'i27',
    'g40',
    'i40',
)


def g27():
    """A000027: The Natural Numbers."""
    yield from itertools.count(1)


def i27(index):
    """A000027: The Natural Numbers."""
    return index


def g40():
    """A000040: The Prime Numbers."""
    yield 0


def i40(index):
    """A000040: The Prime Numbers."""
    return 0

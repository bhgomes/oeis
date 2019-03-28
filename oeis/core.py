# -*- coding: utf-8 -*- #
#
# oeis/core.py
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
from collections.abc import Iterable

# -------------- External Library -------------- #

import requests

# ---------------- oeis Library ---------------- #

from .util import is_int, grouped, Box, BoxObject, subset_box


__all__ = (
    'InvalidID',
    'oeis_name',
    'oeis_number',
    'OEIS_ID_REGEX',
    'SEARCH_FORMAT',
    'ENTRY_FORMAT',
    'B_LIST_FORMAT',
    'query',
    'get_entry',
    'get_b_file',
)


class InvalidID(KeyError):
    """
    Invalid OEIS ID.

    """

    @classmethod
    def from_key(cls, key):
        """Build Exception from Key."""
        return cls('Key {} must be a valid OEIS id.'.format(key))


def _convert_string(key):
    """Convert OEIS String to Integer."""
    if isinstance(key, str):
        key = int(key.upper().strip('A'))
    return key


def oeis_name(key):
    """Get Full Name for OEIS Sequence."""
    try:
        return key.__oeis_name__
    except AttributeError:
        pass
    key = _convert_string(key)
    if is_int(key):
        return 'A{key:06d}'.format(key=key)
    raise InvalidID.from_key(key)


def oeis_number(key):
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


SEARCH_FORMAT = 'https://oeis.org/search?q={term}&fmt=json'


ENTRY_FORMAT = 'https://oeis.org/search?q=id:{index}&fmt=json'


B_LIST_FORMAT = 'https://oeis.org/A{number}/b{number}.txt'


def find_references(text):
    """Find references to OEIS Sequences."""
    return (m.groups() for m in re.finditer(OEIS_ID_REGEX, text))


def raw_query(term, backend=requests):
    """"""
    return subset_box(backend.get(SEARCH_FORMAT.format(term=term)).json(), 'results', original='raw')


def query(term, backend=requests):
    """Search OEIS for Given Term."""
    if term:
        if isinstance(term, Iterable):
            term = ','.join(term)
        return raw_query(term, backend=backend)
    raise TypeError('Type Error.')


def get_entry(index, *, check_name=True, backend=requests):
    """Get OEIS Entry Metadata."""
    if check_name:
        index = oeis_name(index)
    search_result = backend.get(ENTRY_FORMAT.format(index=index)).json()
    if not search_result['count']:
        return Box(raw=search_result)
    return subset_box(search_result, lambda d: d['results'][0], original='raw')


def get_b_file(number, *, check_name=False, backend=requests):
    """Get B-File from OEIS Entry."""
    if check_name:
        number = oeis_name(number)[1:]
    pairs = backend.get(B_LIST_FORMAT.format(number=number)).text.strip().split()
    return BoxObject(tuple(map(int, pairs[1::2])), offset=int(pairs[0]))

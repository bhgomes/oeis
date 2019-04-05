# -*- coding: utf-8 -*- #
#
# tests/test_convention.py
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
Test Naming Convention.

"""

# -------------- External Library -------------- #

import pytest

# ---------------- oeis Library ---------------- #

import oeis
from oeis.base import _convert_string
from oeis.util import is_int
from .core import PYTHON_OBJECTS, random_id_gen, parametrized_ids, match_with


@pytest.mark.parametrize("obj", PYTHON_OBJECTS)
def test_invalid_id(obj):
    if not is_int(obj):
        with pytest.raises(oeis.InvalidID, match=match_with(obj)):
            oeis.name(obj)
        with pytest.raises(oeis.InvalidID, match=match_with(obj)):
            oeis.number(obj)


@parametrized_ids("index", 50)
def test_missing_id(index):
    if not oeis.exists(index):
        with pytest.raises(oeis.MissingID, match=match_with(index)):
            oeis.A(index)
    else:
        assert oeis.A(index)


@parametrized_ids("index", 50)
def test_convert_string(index):
    assert _convert_string(str(index)) == index
    assert _convert_string("A" + str(index)) == index
    assert _convert_string(index) == index


@parametrized_ids("index", 50)
def test_oeis_name_number(index):
    name = oeis.name(index)
    number = oeis.number(index)
    assert isinstance(name, str)
    assert is_int(number)
    assert int(name[1:]) == int(number)


def test_find_references():
    random_ids = map(oeis.name, random_id_gen(100)())
    for index, ref in zip(random_ids, oeis.find_references(".".join(random_ids))):
        assert index == ref

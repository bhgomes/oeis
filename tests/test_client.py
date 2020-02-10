# -*- coding: utf-8 -*- #
#
# tests/test_client.py
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
Test OEIS Client.

"""

# -------------- External Library -------------- #

import pytest
from hypothesis import given
from hypothesis import strategies as st

# ---------------- oeis Library ---------------- #

import oeis
from oeis.util import is_int, BoxObject, Box
from .core import random_ids, PYTHON_OBJECTS, SESSION


# TODO: figure out how to test async functions

# TODO: get sample queries for OEIS searches
SAMPLE_QUERIES = (("1, 2, 3, 4, 5", None), ("1  2  3  4  5", None))


@pytest.mark.parametrize("term, expected", SAMPLE_QUERIES)
def test_oeis_query(term, expected):
    content = oeis.query(term)
    assert content
    if expected:
        assert content == expected


@given(random_ids())
def test_oeis_entry(index):
    content = oeis.entry(index, check_name=True)
    if content:
        assert isinstance(content, Box)
    else:
        assert isinstance(content, BoxObject)
        assert content == None


@pytest.mark.parametrize("obj", PYTHON_OBJECTS)
def test_bad_oeis_entry(obj):
    if not is_int(obj):
        with pytest.raises(Exception):
            oeis.entry(obj)


@given(random_ids())
def test_oeis_exists(index):
    if oeis.client.entry(index):
        assert oeis.exists(index)
    if oeis.client.exists(index):
        assert oeis.entry(index)


@given(st.integers(min_value=999999))
def test_oeis_does_not_exist(number):
    assert not oeis.exists(number)


@given(random_ids())
def test_oeis_b_file(index):
    if oeis.exists(index):
        content = oeis.bfile(index, check_name=True)
        assert isinstance(content, BoxObject)
        assert isinstance(content, tuple)
    else:
        pytest.skip("Missing OEIS Index: {}.".format(index))


@pytest.fixture()
def session():
    return oeis.Session(SESSION)


@pytest.mark.parametrize("term, expected", SAMPLE_QUERIES)
def test_session_query(term, expected, session):
    assert oeis.query(term) == session.query(term)


@given(random_ids())
def test_session_entry(index, session):
    name = oeis.name(index)
    assert oeis.exists(name, check_name=False) == session.exists(name, check_name=False)
    assert oeis.entry(name, check_name=False) == session.entry(name, check_name=False)
    assert oeis.bfile(name, check_name=False) == session.bfile(name, check_name=False)

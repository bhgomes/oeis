# -*- coding: utf-8 -*- #
#
# tests/test_util.py
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
Test OEIS Utilities.

"""

# -------------- External Library -------------- #

import pytest

# ---------------- oeis Library ---------------- #

from oeis.util import *


python_objects = (
    None,
    True,
    False,
    1,
    3.14,
    -3 + 2j,
    "abc",
    [10, 11, 12],
    (),
    {"a": 1, "b": 2},
)


@pytest.mark.parametrize("x", python_objects)
def test_identity(x):
    assert x == identity(x)


@pytest.mark.parametrize("value", python_objects)
def test_value_or(value):
    assert value_or(None, value) == value
    assert value_or(value, value) == value
    test_object = object()
    assert value_or(value, test_object) == (test_object if value is None else value)


@pytest.mark.parametrize("value", python_objects)
def test_value_or_raise(value):
    if value is None:
        with pytest.raises(Exception) as exception_info:
            value_or_raise(value, Exception)
    else:
        assert value_or_raise(value, Exception) == value


def silent_f():
    return


def loud_f():
    raise Exception


def test_except_or_basic():
    assert except_or(silent_f, Exception) is None
    assert except_or(loud_f, Exception) is None
    with pytest.raises(Exception):
        except_or(loud_f, KeyError)


@pytest.mark.parametrize("default", python_objects)
def test_except_or_with_default(default):
    assert except_or(silent_f, Exception, default) is None
    assert except_or(loud_f, Exception, default) == default


def test_getattrmethod():
    assert True


def test_is_int():
    assert is_int(0)
    assert not is_int(0.1)
    assert not is_int("abc")
    assert is_int(numpy.uint(3))
    assert not is_int(numpy.float(3))


def test_empty_function():
    with pytest.raises(TypeError, match=r".* takes 0 positional arguments .*"):
        empty_function(0)
    assert empty_function() is None


def test_empty_generator():
    g = empty_generator()
    assert next(g) is None
    with pytest.raises(StopIteration):
        next(g)


def test_grouped():
    assert True


def test_multi_delimeter():
    assert True


def test_classproperty():
    assert True


def test_box():
    assert True


def test_boxlist():
    assert True


def test_boxobject():
    assert True


def test_subset_box():
    assert True

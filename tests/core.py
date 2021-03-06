# -*- coding: utf-8 -*- #
#
# tests/core.py
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
Test Suite Core.

"""

# -------------- Standard Library -------------- #

import re

# -------------- External Library -------------- #

import requests
from hypothesis import settings
from hypothesis import strategies as st

# ---------------- oeis Library ---------------- #

import oeis


settings.register_profile("base", deadline=None, max_examples=5)
settings.register_profile("ci", deadline=None, max_examples=80)
settings.load_profile("base")


SESSION = requests.Session()


def _func(*args, **kwargs):
    return args, kwargs


class _Class:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


PYTHON_OBJECTS = (
    None,
    0,
    3.14,
    3 + 4j,
    "a",
    "sentence",
    [],
    [1, 2, 3],
    (),
    (1, 2, 3),
    {1, 2, 3},
    {"a": 1, 2: "b", "list": []},
    map(str, range(1, 20)),
    lambda f: None,
    _func,
    _Class(),
    object(),
)


def random_ids(max_id=999999):
    """

    :param max_id:
    :return:
    """
    return st.integers(min_value=1, max_value=max_id)


def random_names(max_id=999999):
    """

    :param max_id:
    :return:
    """
    return random_ids(max_id=max_id).map(oeis.name)


def random_sequences(max_id=999999):
    """

    :param max_id:
    :return:
    """
    return st.builds(oeis.A.safe_load, random_ids(max_id=max_id)).filter(
        lambda n: n is not None
    )


def match_with(obj):
    """
    Regex Match Looking for Object.
    :param obj:
    :return:
    """
    return r".*{}.*".format(re.escape(str(obj)))

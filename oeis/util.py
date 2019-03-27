# -*- coding: utf-8 -*- #
#
# oeis/util.py
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
OEIS Utilities.

"""

# -------------- Standard Library -------------- #

import re
from collections.abc import Iterable

# -------------- External Library -------------- #

import box

# ---------------- oeis Library ---------------- #


def identity(x):
    """"""
    return x


def value_or(value, default):
    """"""
    return value if value is not None else default


def value_or_raise(value, exception):
    """"""
    if value is not None:
        return value
    raise exception


def empty_function():
    """"""
    return


def empty_generator():
    """"""
    yield


def multi_delimeter(*delimiters, flags=0):
    """"""
    return re.compile('|'.join(map(re.escape, delimiters)), flags=flags)


class classproperty(property):
    """Class Property."""

    def __get__(self, obj, objtype=None):
        """Wrap Getter Function."""
        return super().__get__(objtype)

    def __set__(self, obj, value):
        """Wrap Setter Function."""
        return super().__set__(type(obj), value)

    def __delete__(self, obj):
        """Wrap Deleter Function."""
        super().__delete__(type(obj))


class Box(box.Box):
    """
    Box Object.

    """

    @classproperty
    def defaults(cls):
        """"""
        return {'camel_killer_box': True,
                'frozen_box': True,
                'default_box': True,
                'default_box_attr': None}

    def __init__(self, *args, **kwargs):
        """Initialize Box with different Defaults."""
        defaults = self.defaults
        for k, v in self.defaults.items():
            if k in kwargs:
                if v != kwargs[k]:
                    raise TypeError('Box default {key}={value} is permanent.'.format(key=k, value=v))
                kwargs.pop(k)
        super().__init__(*args, **defaults, **kwargs)


class BoxList(box.BoxList):
    """
    BoxList Object.

    """

    def __init__(self, iterable=None, **kwargs):
        """Initialize BoxList with internal Box."""
        super().__init__(iterable=iterable, box_class=Box)
        self.__dict__.update(**kwargs)


def subset_box(dictionary, key, *, original=None):
    """"""
    subset = dictionary[key]
    original_kwargs = Box({original: dictionary}) if original else Box()
    if isinstance(subset, Iterable):
        return BoxList(subset, **original_kwargs)
    return Box(subset, **original_kwargs)

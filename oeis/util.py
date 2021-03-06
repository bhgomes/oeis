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
OEIS Interface Utilities.

"""

# -------------- Standard Library -------------- #

import re
import inspect
from collections.abc import Mapping
from itertools import zip_longest

# -------------- External Library -------------- #

import box
import numpy
import sympy
import wrapt

# ---------------- oeis Library ---------------- #


def identity(x):
    """The Identity function."""
    return x


def value_or(value, default):
    """Returns default if value is exactly None."""
    return value if value is not None else default


def value_or_raise(value, exception):
    """Raise exception if value is exactly None."""
    if value is not None:
        return value
    raise exception


def except_or(f, exception, *default):
    """Catch Exception and Return Default."""
    try:
        return f()
    except exception:
        if default:
            return default[0]
        return


def getattrmethod(obj, attr, *default):
    """Get Attribute or Method Value: whatever works."""
    try:
        value = getattr(obj, attr)
        return value() if inspect.ismethod(value) else value
    except (AttributeError, TypeError) as exception:
        if default:
            if len(default) != 1:
                return TypeError(
                    f"getattrmethod expected at most 3 arguments, got {2 + len(default)}"
                )
            return default[0]
        raise exception


def is_int(n):
    """Check if number is an integer."""
    return isinstance(n, (int, numpy.integer, sympy.numbers.Integer))


def empty_function():
    """Function that does nothing."""
    return


def empty_generator():
    """Generator that yields nothing."""
    yield


def grouped(iterable, n, default=None):
    """Group Iterable into parts."""
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=default, *args)


def multi_delimiter(*delimiters, flags=0):
    """Constructs a multi-delimiter for splitting with Regex."""
    return re.compile("|".join(map(re.escape, delimiters)), flags=flags)


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
        """Default arguments to the Box."""
        return {
            "camel_killer_box": True,
            "frozen_box": True,
            "default_box": True,
            "default_box_attr": None,
        }

    def __init__(self, *args, **kwargs):
        """Initialize Box with custom Defaults."""
        defaults = self.defaults
        for k, v in self.defaults.items():
            if k in kwargs:
                if v != kwargs[k]:
                    raise TypeError(
                        "Box default {key}={value} is permanent.".format(key=k, value=v)
                    )
                kwargs.pop(k)
        super().__init__(*args, **defaults, **kwargs)


class BoxList(box.BoxList):
    """
    BoxList Object.

    """

    def __init__(self, iterable=None, box_class=Box, **kwargs):
        """
        Initialize BoxList with custom Box.

        :param iterable:
        :param box_class:
        :param kwargs:
        """
        super().__init__(iterable=iterable, box_class=box_class)
        self.__dict__.update(**kwargs)


class BoxObject(wrapt.ObjectProxy):
    """
    Wrapper for any Python object with a Box as __dict__.
    """

    def __init__(self, wrapped=None, *args, **kwargs):
        """
        Initialize Box Object with __dict__ as a Box.

        :param wrapped:
        :param args:
        :param kwargs:
        """
        super(BoxObject, self).__init__(wrapped)
        box_class = kwargs.pop("box_class", Box)
        try:
            base_dict = super(BoxObject, self).__getattr__("__dict__")
            if args:
                raise TypeError(
                    "Cannot pass dictionary arguments when "
                    "internal object has __dict__ attributes. "
                    "Pass arguments by keyword instead."
                )
            box_dict = box_class(base_dict, **kwargs)
        except AttributeError:
            box_dict = box_class(*args, **kwargs)
        super(BoxObject, self).__setattr__("__dict__", box_dict)

    def __call__(self, *args, **kwargs):
        """
        Call Method for Callable Objects.

        :param args:
        :param kwargs:
        :return:
        """
        return self.__wrapped__(*args, **kwargs)

    def __getattr__(self, name):
        """
        Get Attribute from Wrapped Object or from Box.

        :param name:
        :return:
        """
        try:
            return super(BoxObject, self).__getattr__(name)
        except AttributeError as error:
            try:
                return self.__dict__[name]
            except KeyError:
                raise error

    def __setattr__(self, name, value):
        """
        Set Attribute in Wrapped Object or Box.

        :param name:
        :param value:
        :return:
        """
        if name == "__dict__":
            raise TypeError("cannot set __dict__")
        elif hasattr(self.__wrapped__, name):
            setattr(self.__wrapped__, name, value)
        else:
            self.__dict__[name] = value

    def __delattr__(self, name):
        """
        Delete Attribute in Wrapped Object or Box.

        :param name:
        :return:
        """
        if name == "__dict__":
            super(BoxObject, self).__setattr__(
                "__dict__", getattr(self.__wrapped__, "__dict__", {})
            )
        else:
            try:
                delattr(self.__wrapped__, name)
            except AttributeError as error:
                try:
                    del self.__dict__[name]
                except KeyError:
                    raise error


def subset_box(total, key=identity, *, origin_name=None):
    """Get subset of mapping type as a Box or BoxObject."""
    subset = key(total)
    kwargs = Box({origin_name: total}) if origin_name else Box()
    if isinstance(subset, Mapping):
        return Box(subset, **kwargs)
    return BoxObject(subset, **kwargs)


def import_package(name):
    """Import Package."""
    try:
        return __import__(name), True
    except ImportError:
        return BoxObject(name), False

# -*- coding: utf-8 -*- #
#
# oeis/sequence.py
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
OEIS Sequences.

"""

# -------------- Standard Library -------------- #

import re
from collections.abc import MutableMapping
from copy import deepcopy
from datetime import datetime
from itertools import chain, groupby, islice
from functools import partial
import inspect

# -------------- External Library -------------- #

from wrapt import ObjectProxy

# ---------------- oeis Library ---------------- #

from .base import name as oeis_name
from .base import number as oeis_number
from .base import find_references, MissingID
from .client import entry as oeis_entry
from .client import bfile as oeis_bfile
from .util import is_int, value_or, empty_generator, Box, BoxList


__all__ = ("Sequence", "SequenceFactory", "Registry")


def _slice_details(f, *args, **kwargs):
    """
    Get Slice Details of a Function.

    :param f:
    :param args:
    :param kwargs:
    :return:
    """
    if inspect.isgeneratorfunction(f):
        gen = f(*args, **kwargs)
        return type(gen), 3, partial(islice, gen)
    if inspect.isgenerator(f):
        return type(f), 3, partial(islice, f)
    if inspect.ismethod(f) or inspect.isfunction(f):
        signature = inspect.signature(f)
        argument_count = len(signature.parameters)
        if argument_count in (1, 3):
            for parameter in signature.parameters.values():
                if parameter.kind != inspect.Parameter.POSITIONAL_OR_KEYWORD:
                    return type(f), 0, None
            return type(f), argument_count, f
    return type(f), 0, None


class Sequence(ObjectProxy):
    """
    OEIS Sequence Function Wrapper.

    """

    def __init__(self, number, generator=None, *, meta=None):
        """
        Initialize Proxy.

        :param number:
        :param generator:
        :param meta:
        """
        super().__init__(value_or(generator, empty_generator))
        self._self_number = number
        self._self_meta = value_or(meta, Box())

    @classmethod
    def from_dict(cls, meta):
        """
        Create Sequence from Metadata Dictionary.

        :param meta:
        :return:
        """
        return cls(oeis_number(meta["number"]), meta=meta)

    @classmethod
    def from_sequence(cls, sequence, new_generator=None, *, new_meta=None, copy=False):
        """
        Generate Sequence from Existing Sequence.

        :param sequence:
        :param new_generator:
        :param new_meta:
        :param copy:
        :return:
        """
        if not (new_generator or new_meta):
            return deepcopy(sequence) if copy else sequence
        generator = value_or(new_generator, sequence.__wrapped__)
        meta = value_or(new_meta, sequence.meta)
        return cls(sequence.number, generator, meta=meta)

    def __call__(self, *args, **kwargs):
        """
        Call Internal Generator.

        :param args:
        :param kwargs:
        :return:
        """
        return self.__wrapped__(*args, **kwargs)

    def get(
        self,
        index,
        *args,
        cache_result=False,
        ignore_offset=False,
        ignore_sample=False,
        **kwargs
    ):
        """
        Get Index into Sequence.

        :param index:
        :param args:
        :param cache_result:
        :param ignore_offset:
        :param ignore_sample:
        :param kwargs:
        :return:
        """
        if cache_result:
            return NotImplemented

        if is_int(index):
            index = slice(index)
        if isinstance(index, slice):
            start, stop, step = index.start, index.stop, index.step
            if not ignore_offset:
                start = start - self.offset
                if stop:
                    stop = stop - self.offset
        else:
            raise TypeError("expected integer or slice")

        gen_type, argument_count, gen = _slice_details(self.generator, *args, **kwargs)

        if not ignore_sample:
            sample_length = len(self.sample)
            after_sample = stop - sample_length
            if start < sample_length:
                yield from self.sample[start : min(stop, sample_length) : step]
            if after_sample < 0:
                return
            start = sample_length
            stop = stop

        if argument_count == 3:
            yield from gen(start, stop, step)
        if argument_count == 1:
            if stop is None and step is None:
                yield gen(start)
            yield from map(gen, range(start, stop, step))

        raise TypeError("invalid generator")

    def __getitem__(self, index, *args):
        """
        Get Index into Sequence.

        :param index:
        :param args:
        :return:
        """
        return self.get(index, *args)

    @property
    def number(self):
        """Get Sequence Number."""
        return self._self_number

    @property
    def short_name(self):
        """Get Sequence Short Name."""
        return "A{number}".format(number=self.number)

    @property
    def name(self):
        """Get Sequence Full Name."""
        return "A{number:06d}".format(number=self.number)

    @property
    def website(self):
        """Get Website for Sequence."""
        return "https://oeis.org/{}".format(self.name)

    @property
    def __oeis_name__(self):
        """Standard OEIS Name."""
        return self.name

    @property
    def __oeis_number__(self):
        """Standard OEIS Number."""
        return self.number

    @property
    def meta(self):
        """Get Full Metadata Box."""
        return self._self_meta

    @property
    def offset(self):
        """Get Sequence Offset."""
        return int(self.meta.offset.split(",")[0])

    @property
    def description(self):
        """Get Sequence Description."""
        return self.meta.name

    @property
    def sample(self):
        """Get Cached Sample of the Sequence."""
        if not hasattr(self, "_self_sample"):
            self._self_sample = list(map(int, self.meta.data.split(",")))
            self._self_with_bfile = False
        return self._self_sample

    def sample_append(self, value):
        """Append to Sequence Sample."""
        self.sample.append(value)

    def sample_extend(self, values):
        """Extend Sample Sequence."""
        self.sample.extend(values)

    def sample_reset(self):
        """Reset Sequence Sample to Metadata Default."""
        if hasattr(self, "_self_sample"):
            del self._self_sample
            self._self_with_bfile = False

    @property
    def with_bfile(self):
        """Check if B-File is Loaded into Sample."""
        if not hasattr(self, "_self_with_bfile"):
            self._self_with_bfile = False
        return self._self_with_bfile

    @property
    def formulas(self):
        """Get Formulas for Sequence."""
        return self.meta.formula

    @classmethod
    def _parse_programs(cls, others):
        """Parse Sample Program List."""
        if not hasattr(cls, "_program_regex"):
            cls._program_regex = re.compile(
                r"^\(([^\(\)]*)+?\).*$", re.MULTILINE | re.UNICODE
            )
        last_key = None

        def key(line):
            nonlocal last_key
            try:
                last_key = cls._program_regex.match(line).groups()[0]
            except AttributeError:
                return last_key
            return last_key

        clean = lambda k: lambda s: s.replace("({})".format(k), "").strip()
        return {k.lower(): tuple(map(clean(k), g)) for k, g in groupby(others, key=key)}

    @property
    def programs(self):
        """Get OEIS Sample Programs."""
        return Box(
            maple=self.meta.maple,
            mathematica=self.meta.mathematica,
            **self._parse_programs(self.meta.program)
        )

    @property
    def keywords(self):
        """Get OEIS Keywords."""
        return self.meta.keyword.split(",")

    @property
    def recycled(self):
        """Check if Sequence is Recycled."""
        return "recycled" in self.keywords

    @property
    def modified(self):
        """Get Last Modified Time."""
        return datetime.fromisoformat(self.meta.time)

    @property
    def created(self):
        """Get Created Time."""
        return datetime.fromisoformat(self.meta.created)

    @classmethod
    def _find_chain_references(cls, text):
        """Find references to OEIS Sequences."""
        return tuple(chain.from_iterable(find_references(text)))

    @classmethod
    def _find_xref_keys(cls, xref):
        """Find Cross Reference Keys."""
        return tuple((cls._find_chain_references(entry), entry) for entry in xref)

    @property
    def cross_references(self):
        """Get Cross References for Sequence."""
        if not hasattr(self, "_self_xref"):
            xref = self.meta.xref
            if xref:
                self._self_xref = self._find_xref_keys(xref)
            else:
                self._self_xref = tuple()
        return self._self_xref

    @classmethod
    def _parse_comments(cls, comments):
        """Parse Comments for References."""
        for comment in comments:
            text = comment.strip()
            yield dict(text=text, references=cls._find_chain_references(text))

    @property
    def comments(self):
        """Get Comments for Sequence."""
        if not hasattr(self, "_self_comments"):
            comments = self.meta.comment
            if comments:
                self._self_comments = BoxList(tuple(self._parse_comments(comments)))
            else:
                self._self_comments = BoxList()
        return self._self_comments

    @property
    def finite(self):
        """Get Finiteness of Sequence."""
        return NotImplemented


class SequenceFactory:
    """
    OEIS Sequence Factory.

    """

    __slots__ = ("session", "cache", "always_cache")

    def __init__(self, *, factory=dict, session=None, always_cache=False):
        """
        Initialize Sequence Factory.

        :param factory:
        :param session:
        :param always_cache:
        """
        self.cache = factory()
        self.session = session
        self.always_cache = always_cache

    @classmethod
    def from_cache(cls, cache, *, session=None, always_cache=False):
        """
        Make Sequence Factory from Pre-loaded Cache.

        :param cache:
        :param session:
        :param always_cache:
        :return:
        """
        return cls(factory=lambda: cache, session=session, always_cache=always_cache)

    def __reduce__(self):
        """
        Reduce Sequence Factory for Pickling.

        :return:
        """
        return self.__class__, (self.cache, self.session, self.always_cache)

    def __eq__(self, other):
        """
        Equality of SequenceFactory.

        :param other:
        :return:
        """
        if isinstance(other, type(self)):
            return self.__reduce__() == other.__reduce__()
        return NotImplemented

    def clear(self):
        """
        Clear Cache.

        :return:
        """
        self.cache.clear()

    def __len__(self):
        """
        Size of Cache.

        :return:
        """
        return len(self.cache)

    def __iter__(self):
        """
        Iterate Through Cache.

        :return:
        """
        return iter(self.cache)

    def __contains__(self, item):
        """
        Check if item is Stored in the Cache.

        :param item:
        :return:
        """
        return item in self.cache

    def load_meta(self, key, *, check_name=False):
        """Load Metadata Dictionary from Loader."""
        return oeis_entry(key, self.session, check_name=check_name)

    def _extend_from_bfile(self, key, sequence, *, check_name=False):
        """
        Extend Sample Data for Sequence from B-File if possible.

        :param key:
        :param sequence:
        :param check_name:
        :return:
        """
        data = oeis_bfile(key, self.session, check_name=check_name)
        if data:
            sequence.sample_extend(data[len(sequence.sample) :])
            sequence._self_with_bfile = True
        return sequence

    def load(self, key, *, cache_result=True, with_bfile=False):
        """
        Load Sequence with Default Caching.

        :param key:
        :param cache_result:
        :param with_bfile:
        :return:
        """
        key = oeis_name(key)
        try:
            previous = self.cache[key]
            if with_bfile and not previous.with_bfile:
                return self._extend_from_bfile(key, previous, check_name=False)
            return previous
        except KeyError:
            pass
        meta = self.load_meta(key, check_name=False)
        if not meta:
            raise MissingID.from_key(key)
        if with_bfile:
            entry = self._extend_from_bfile(
                key, Sequence.from_dict(meta), check_name=False
            )
        else:
            entry = Sequence.from_dict(meta)
        if cache_result or self.always_cache:
            self.cache[key] = entry
            return self.cache[key]
        return entry

    def __call__(self, key, *args, cache_result=False, **kwargs):
        """
        Load Sequence without Caching by Default.

        :param key:
        :param args:
        :param cache_result:
        :param kwargs:
        :return:
        """
        return self.load(
            key, *args, cache_result=cache_result or self.always_cache, **kwargs
        )


class Registry(MutableMapping):
    """
    Sequence Registry.

    """

    __slots__ = ("_factory",)

    @classmethod
    def from_factory(cls, factory):
        """
        Make Registry from Pre-existing Factory.

        :param factory:
        :return:
        """
        obj = object.__new__(cls)
        obj._factory = factory
        return obj

    def __new__(cls, *, cache_factory=dict, session=None):
        """
        Make new Registry.

        :param cache_factory:
        :param session:
        :return:
        """
        return cls.from_factory(SequenceFactory(factory=cache_factory, session=session))

    def __repr__(self):
        """Get Registry Representation."""
        return "{cls}{cache}".format(
            cls=type(self).__name__, cache=tuple(self.internal_cache)
        )

    @property
    def internal_cache(self):
        """Get Factory Cache."""
        return self._factory.cache

    def __getattr__(self, name):
        """Get Element from Cache as AttributeError."""
        try:
            return self[name]
        except KeyError:
            raise AttributeError("Missing Key: {}.".format(name))

    def __contains__(self, key):
        """Check Containment of OEIS Key."""
        return oeis_name(key) in self.internal_cache

    def __getitem__(self, key):
        """Get Element from Internal Cache."""
        return self.internal_cache[oeis_name(key)]

    def __setitem__(self, key, value):
        """Set Element of Internal Cache."""
        self.internal_cache[key] = value

    def __delitem__(self, key):
        """Delete Element from Internal Cache."""
        del self.internal_cache[oeis_name(key)]

    def __iter__(self):
        """Return Iterator to Internal Cache."""
        return iter(self.internal_cache)

    def __len__(self):
        """Get Length of Internal Cache."""
        return len(self.internal_cache)

    def clear(self):
        """Clear Factory."""
        return self._factory.clear()

    def register(self, key, generator=None, *, meta=None):
        """
        Register Sequence through Factory.

        :param key:
        :param generator:
        :param meta:
        :return:
        """
        try:
            cached_value = self[key]
            if meta and cached_value.meta == meta:
                return Sequence.from_sequence(cached_value, generator)
            generator = value_or(generator, cached_value.__wrapped__)
        except KeyError:
            pass
        key = oeis_name(key)
        if meta is True:
            meta = self._factory.load_meta(key, check_name=False)
        number = oeis_number(key)
        if meta and number != meta.number:
            raise ValueError(
                "OEIS numbers don't match: "
                "{} should be {}".format(number, meta.number)
            )
        self[key] = Sequence(number, generator=generator, meta=meta)
        return self.internal_cache[key]

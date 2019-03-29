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
from itertools import chain, groupby

# -------------- External Library -------------- #

from wrapt import ObjectProxy

# ---------------- oeis Library ---------------- #

from .base import find_references
from .base import name as oeis_name
from .base import number as oeis_number
from .client import entry as oeis_entry
from .util import value_or, empty_generator, Box, BoxList, BoxObject


__all__ = ("Sequence", "SequenceFactory", "Registry")


class Sequence(ObjectProxy):
    """
    OEIS Sequence Function Wrapper.

    """

    def __init__(self, number, generator=None, *, index_function=None, meta=None):
        """Initialize Proxy."""
        # TODO: check that the generator is callable
        # TODO: make the generation function optional between index and gen or both?
        super().__init__(value_or(generator, empty_generator))
        self._self_number = number
        self._self_meta = value_or(meta, Box())
        if index_function:
            self._self_has_index_function = True
            self._self_index_function = index_function
        else:
            self._self_has_index_function = False
            self._self_index_function = self.__getitem__

    @classmethod
    def from_dict(cls, meta):
        """Create Sequence from Metadata Dictionary."""
        return cls(oeis_number(meta["number"]), meta=meta)

    @classmethod
    def from_sequence(
        cls,
        sequence,
        new_generator=None,
        *,
        new_index_function=None,
        new_meta=None,
        copy=False
    ):
        """Generate Sequence from Existing Sequence."""
        if not any((new_generator, new_index_function, new_meta)):
            return deepcopy(sequence) if copy else sequence
        index_function = value_or(
            new_index_function,
            sequence.index_function if sequence._self_has_index_function else None,
        )
        generator = value_or(new_generator, sequence.__wrapped__)
        meta = value_or(new_meta, sequence.meta)
        return cls(sequence.number, generator, index_function=index_function, meta=meta)

    @property
    def index_function(self):
        """Get Index Function Instead of Generator."""
        return self._self_index_function

    def __call__(self, *args, **kwargs):
        """"""
        return self.__wrapped__(*args, **kwargs)

    def get(self, index, *args, cache_result=False, **kwargs):
        """Get Index into Sequence."""
        # TODO:
        # if isinstance(index, int):
        #     index = slice(index, index + 1, 1)
        # start, stop, step = index

        # TODO: do index checking here not in the wrapped function

        offset = self.offset[0]
        new_index = index - offset
        if new_index < len(self.sample):
            return self.sample[new_index]
        if self._self_has_index_function:
            return self.index_function(new_index - offset, *args, **kwargs)
        generator = self(*args, **kwargs)
        for _ in range(offset, index):
            next(generator)
        return next(generator)

    def __getitem__(self, index):
        """Get Index into Sequence."""
        return self.get(index)

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
        return tuple(map(int, self.meta.offset.split(",")))

    @property
    def description(self):
        """Get Sequence Description."""
        return self.meta.name

    @property
    def sample(self):
        """Get Cached Sample of the Sequence."""
        if not hasattr(self, "_self_sample"):
            self._self_sample = list(map(int, self.meta.data.split(",")))
        return self._self_sample

    def sample_append(self, value):
        """Append to Sequence Sample."""
        self._self_sample.append(value)

    def sample_extend(self, values):
        """Extend Sample Sequence."""
        self._self_sample.extend(values)

    def sample_reset(self):
        """Reset Sequence Sample to Metadata Default."""
        del self._self_sample

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
        maple = self.meta.maple
        mathematica = self.meta.mathematica
        return Box(
            maple=maple,
            mathematica=mathematica,
            **self._parse_programs(self.meta.program)
        )

    @property
    def keywords(self):
        """Get OEIS Keywords."""
        return self.meta.keyword.split(",")

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

    __slots__ = ("_session", "_cache", "always_cache")

    def __init__(self, *, factory=dict, session=None, always_cache=False):
        """Initialize Sequence Factory."""
        self._session = session
        self._cache = factory()
        self.always_cache = always_cache

    @classmethod
    def from_cache(cls, cache, *, session=None, always_cache=False):
        """Make Sequence Factory from Pre-loaded Cache."""
        return cls(factory=lambda: cache, session=session, always_cache=always_cache)

    def __reduce__(self):
        """Reduce Sequence Factory for Pickleing."""
        return (self.__class__, (self._session, self._cache, self.always_cache))

    def clear(self):
        """Clear Cache."""
        self._cache.clear()

    @property
    def cache(self):
        """Get Internal Cache Object."""
        return self._cache

    def load_meta(self, key, *, check_name=False):
        """Load Metadata Dictionary from Loader."""
        return oeis_entry(key, self._session, check_name=check_name)

    def load(self, key, *, cache_result=True, preload_sample=None):
        """Load Sequence with Default Caching."""
        key = oeis_name(key)
        try:
            return self._cache[key]
        except KeyError:
            pass
        try:
            meta = self.load_meta(key, check_name=False)
            if not meta:
                raise Exception
            entry = Sequence.from_dict(meta)
        except Exception as e:  # TODO: Figure this out
            raise e
        if cache_result or self.always_cache:
            self._cache[key] = entry
        return entry

    def __call__(self, key, *args, cache_result=False, **kwargs):
        """Load Sequence without Caching by Default."""
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
        """Make Registry from Pre-existing Factory."""
        obj = object.__new__(cls)
        obj._factory = factory
        return obj

    def __new__(cls, *, cache_factory=dict, session=None):
        """Make new Registry."""
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
        """Register Sequence through Factory."""
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

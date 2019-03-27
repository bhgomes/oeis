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
from collections import namedtuple
from collections.abc import Generator, MutableMapping, Iterable
from datetime import datetime
from itertools import chain, groupby

# -------------- External Library -------------- #

import requests
from wrapt import ObjectProxy

# ---------------- oeis Library ---------------- #

from .util import (
    value_or, empty_generator, multi_delimeter, Box, BoxList, subset_box
)


__all__ = (
    'oeis_name',
    'oeis_number',
    'OEIS_NUMBER_REGEX',
    'SEARCH_FORMAT',
    'ENTRY_FORMAT',
    'format_search',
    'format_entry',
    'search',
    'load_entry',
    'get_entry_details',
    'Sequence',
    'SequenceFactory',
    'Registry'
)


def _convert_string(key):
    """"""
    if isinstance(key, str):
        key = int(key.upper().strip('A'))
    return key


def oeis_name(key):
    """"""
    key = _convert_string(key)
    if isinstance(key, int):
        return 'A' + str(key)
    raise KeyError('Key {} must be a valid OEIS id.'.format(key))


def oeis_number(key):
    """"""
    key = _convert_string(key)
    if isinstance(key, int):
        return key
    raise KeyError('Key {} must be a valid OEIS id.'.format(key))


OEIS_NUMBER_REGEX = re.compile(r"(A\d+)", re.MULTILINE | re.UNICODE)


SEARCH_FORMAT = 'https://oeis.org/search?fmt=json&q={term}'


ENTRY_FORMAT = 'http://oeis.org/search?q=id:{index}&fmt=json'


def format_search(term):
    """"""
    return SEARCH_FORMAT.format(term=term)


def format_entry(index):
    """"""
    return ENTRY_FORMAT.format(index=index)


def search(term, backend=requests):
    """"""
    if term:
        if isinstance(term, Iterable):
            term = ','.join(term)
        return subset_box(backend.get(format_search(term)).json(), 'results', original='raw')
    raise TypeError('Type Error.')


def load_entry(index, *, check_name=True, backend=requests):
    """"""
    if check_name:
        index = oeis_name(index)
    return subset_box(backend.get(format_entry(index)).json(), 'results', original='raw')


def get_entry_details(index, *, check_name=False, backend=requests):
    """"""
    search_result = load_entry(index, check_name=check_name, backend=backend)
    try:
        entry = search_result[0]
    except Exception:
        raise
    return entry


class Sequence(ObjectProxy):
    """"""

    def __init__(self, number, generator=None, *, index_function=None, meta=None):
        """"""
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
        """"""
        return cls(oeis_number(meta['number']), meta=meta)

    @classmethod
    def from_json(cls, json_object):
        """"""
        return cls.from_dict(json_object)

    @classmethod
    def from_sequence(cls, sequence, new_generator=None, *, new_index_function=None, new_meta=None):
        """"""
        if not any((new_generator, new_index_function, new_meta)):
            return sequence
        index_function = value_or(new_index_function,
                                  sequence.index_function if sequence._self_has_index_function else None)
        generator = value_or(new_generator, sequence.__wrapped__)
        meta = value_or(new_meta, sequence.meta)
        return cls(sequence.number,
                   generator,
                   index_function=index_function,
                   meta=meta)

    @property
    def index_function(self):
        """"""
        return self._self_index_function

    def __call__(self, *args, **kwargs):
        """"""
        return self.__wrapped__(*args, **kwargs)

    def get(self, index, *args, cache_result=False, **kwargs):
        """"""
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
        else:
            generator = self(*args, **kwargs)
            for i in range(offset, index):
                next(generator)
            return next(generator)

    def __getitem__(self, index):
        """"""
        return self.get(index)

    @property
    def number(self):
        """"""
        return self._self_number

    @property
    def short_name(self):
        """"""
        return 'A{number}'.format(number=self.number)

    @property
    def name(self):
        """"""
        return 'A{number:06d}'.format(number=self.number)

    @property
    def meta(self):
        """"""
        return self._self_meta

    @property
    def offset(self):
        """"""
        return tuple(map(int, self.meta.offset.split(',')))

    @property
    def description(self):
        """"""
        return self.meta.name

    @property
    def sample(self):
        """"""
        if not hasattr(self, '_self_sample'):
            self._self_sample = tuple(map(int, self.meta.data.split(',')))
        return self._self_sample

    def sample_append(self, value):
        """"""
        self._self_sample.append(value)

    def sample_extend(self, values):
        """"""
        self._self_sample.extend(values)

    def sample_reset(self):
        """"""
        del self._self_sample

    @property
    def formulas(self):
        """"""
        return self.meta.formula

    @classmethod
    def _parse_programs(cls, others):
        """"""
        if not hasattr(cls, '_program_regex'):
            cls._program_regex = re.compile(r"^\(([^\(\)]*)+?\).*$", re.MULTILINE | re.UNICODE)
        last_key = None
        def key(s):
            global last_key
            try:
                last_key = cls._program_regex.match(s).groups()[0]
            except AttributeError:
                return last_key
            return last_key
        clean = lambda k: lambda s: s.replace('({})'.format(k), '').strip()
        return {k.lower(): tuple(map(clean(k), g)) for k, g in groupby(others, key=key)}

    @property
    def programs(self):
        """"""
        maple = self.meta.maple
        mathematica = self.meta.mathematica
        return Box(maple=maple,
                   mathematica=mathematica,
                   **self._parse_programs(self.meta.program))

    @property
    def keywords(self):
        """"""
        return self.meta.keyword.split(',')

    @property
    def time(self):
        """"""
        return datetime.fromisoformat(self.meta.time)

    @property
    def created(self):
        """"""
        return datetime.fromisoformat(self.meta.created)

    @classmethod
    def _find_references(cls, text):
        """"""
        return tuple(chain.from_iterable((m.groups() for m in re.finditer(OEIS_NUMBER_REGEX, text))))

    @classmethod
    def _find_xref_keys(cls, xref):
        """"""
        return tuple((cls._find_references(entry), entry) for entry in xref)

    @property
    def cross_references(self):
        """"""
        if not hasattr(self, '_self_xref'):
            xref = self.meta.xref
            if xref:
                self._self_xref = self._find_xref_keys(xref)
            else:
                self._self_xref = tuple()
        return self._self_xref

    @classmethod
    def _parse_comments(cls, comments):
        """"""
        for comment in comments:
            text = comment.strip()
            yield dict(text=text, references=cls._find_references(text))

    @property
    def comments(self):
        """"""
        if not hasattr(self, '_self_comments'):
            comments = self.meta.comment
            if comments:
                self._self_comments = BoxList(tuple(self._parse_comments(comments)))
            else:
                self._self_comments = BoxList()
        return self._self_comments

    @property
    def finite(self):
        """"""
        return NotImplemented


class SequenceFactory:
    """"""

    __slots__ = ('_loader', '_cache')

    def __init__(self, *, factory=dict, loader=requests):
        """"""
        self._loader = loader
        self._cache = factory()

    def __call__(self, key, *, cache_result=False):
        """"""
        return self.load(key, cache_result=cache_result)

    def load_meta(self, key, *, check_name=False):
        """"""
        return get_entry_details(key, check_name=check_name, backend=self._loader)

    def load(self, key, *, cache_result=True, preload_sample=None):
        """"""
        key = oeis_name(key)
        try:
            return self._cache[key]
        except KeyError:
            pass
        try:
            entry = Sequence.from_dict(self.load_meta(key, check_name=False))
        except Exception:  # TODO: Figure this out
            raise
        if cache_result:
            self._cache[key] = entry
        return entry

    def clear(self):
        """"""
        self._cache.clear()

    @property
    def cache(self):
        """"""
        return self._cache


class Registry(MutableMapping):
    """"""

    __slots__ = ('_factory', )

    @classmethod
    def from_factory(cls, factory):
        """"""
        obj = object.__new__(cls)
        obj._factory = factory
        return obj

    def __new__(cls, *, cache_factory=dict, loader=requests):
        """"""
        return cls.from_factory(SequenceFactory(factory=cache_factory, loader=loader))

    def __repr__(self):
        """"""
        return '{cls}{cache}'.format(cls=type(self).__name__, cache=tuple(self.internal_cache))

    @property
    def internal_cache(self):
        """"""
        return self._factory.cache

    def __getattr__(self, name):
        """"""
        key = oeis_name(name)
        if key in self.keys():
            return self.internal_cache[key]
        raise AttributeError('Missing Key: {}.'.format(name))

    def __getitem__(self, key):
        """"""
        return self.internal_cache[oeis_name(key)]

    def __setitem__(self, key, value):
        """"""
        self.internal_cache[key] = value

    def __delitem__(self, key):
        """"""
        del self.internal_cache[oeis_name(key)]

    def __iter__(self):
        """"""
        return iter(self.internal_cache)

    def __len__(self):
        """"""
        return len(self.internal_cache)

    def clear(self):
        """"""
        return self._factory.clear()

    def register(self, key, generator=None, *, meta=None):
        """"""
        try:
            cached_value = self[key]
            if meta and cached_value.meta == meta:
                return Sequence.from_sequence(cached_value, generator)
            else:
                generator = value_or(generator, cached_value.__wrapped__)
        except KeyError:
            pass
        key = oeis_name(key)
        if meta is True:
            meta = self._factory.load_meta(key, check_name=False)
        number = oeis_number(key)
        if meta and number != meta.number:
            raise ValueError("OEIS numbers don't match: "
                             "{number} should be {meta_number}".format(number=number, meta_number=meta.number))
        self[key] = Sequence(number, generator=generator, meta=meta)
        return self.internal_cache[key]

# -*- coding: utf-8 -*- #
#
# tests/test_sequence.py
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
Test OEIS Sequences.

"""

# -------------- Standard Library -------------- #

from datetime import datetime
from functools import partial

# -------------- External Library -------------- #

import pytest
import requests

# ---------------- oeis Library ---------------- #

import oeis
from oeis.sequence import _slice_details, Sequence, SequenceFactory, Registry
from oeis.util import Box, BoxObject
from .core import (
    parametrized_ids,
    parametrized_sequences,
    random_id_gen,
    random_sequences,
)


def index_function(index):
    return index


def explicit_slice_function(start, stop, step=None):
    return start, stop, step


def generator_function():
    yield


def too_many_arguments(a, b, c, d, e, f):
    return a, b, c, d, e, f


def wrong_signature1(a, *args, **kwargs):
    return a, args, kwargs


def wrong_signature2(a, b=1, *, c=1):
    return a, b, c


def wrong_signature3(*, a=1, b=1, c=1):
    return a, b, c


def wrong_signature4(*, a=1, **kwargs):
    return a, kwargs


BAD_SIGNATURES = (
    None,
    too_many_arguments,
    wrong_signature1,
    wrong_signature2,
    wrong_signature3,
    wrong_signature4,
)


def test_slice_details():
    assert _slice_details(index_function) == (type(index_function), 1, index_function)
    assert _slice_details(explicit_slice_function) == (
        type(explicit_slice_function),
        3,
        explicit_slice_function,
    )
    generator_function_slice = _slice_details(generator_function)
    generator = generator_function()
    assert generator_function_slice[0] == type(generator)
    assert generator_function_slice[1] == 3
    assert isinstance(generator_function_slice[2], partial)
    generator_slice = _slice_details(generator)
    assert generator_slice[0] == type(generator)
    assert generator_slice[1] == 3
    assert isinstance(generator_slice[2], partial)
    for f in BAD_SIGNATURES:
        assert _slice_details(f) == (type(f), 0, None)


@parametrized_ids("index", 50)
def test_initialization(index):
    empty_generator_sequence = Sequence(index)
    assert empty_generator_sequence.number == index
    assert empty_generator_sequence.short_name == "A{}".format(index)
    assert empty_generator_sequence.name == oeis.name(index)
    assert empty_generator_sequence.meta == Box()


@parametrized_sequences("sequence", 5)
def test_dunder_attributes(sequence):
    assert sequence.__oeis_name__ == sequence.name
    assert sequence.__oeis_number__ == sequence.number


def test_meta():
    assert True


def test_sample():
    assert True


def test_bfile():
    assert True


def test_programs():
    assert True


@parametrized_sequences("sequence", 5)
def test_timestamps(sequence):
    assert isinstance(sequence.modified, datetime)
    assert isinstance(sequence.created, datetime)


def test_cross_references():
    assert True


def test_comments():
    assert True


def test_finite():
    assert True


def test_factory_from_cache():
    sequences = list(random_sequences(50))
    session = requests.Session()
    blank_factory = SequenceFactory(session=session)
    cache = {}
    for sequence in sequences:
        blank_factory.cache[sequence.name] = sequence
        cache[sequence.name] = sequence
    from_cache = SequenceFactory.from_cache(cache, session=session)
    assert blank_factory == from_cache


def make_factory(count=30):
    factory = SequenceFactory(session=requests.Session(), always_cache=True)
    for index in list(random_id_gen(count)()):
        try:
            factory.load(index)
        except oeis.MissingID:
            pass
    return factory


def test_factory_dunder_reduce():
    factory = make_factory()
    assert factory.__reduce__() == (
        type(factory),
        (factory.cache, factory.session, factory.always_cache),
    )


def test_factory_as_cache_behavior():
    factory = make_factory()
    assert len(factory) == len(factory.cache)
    assert list(iter(factory)) == list(iter(factory.cache))
    for key in factory.cache.keys():
        assert key in factory
    factory.clear()
    assert len(factory) == 0
    assert len(factory.cache) == 0


def test_sequence_loading():
    factory = make_factory(0)
    for index in map(oeis.name, list(random_id_gen(50)())):
        meta = factory.load_meta(index)
        if not oeis.exists(index):
            assert isinstance(meta, BoxObject)
            assert meta == None
        else:
            assert isinstance(meta, Box)
            assert isinstance(meta.raw, dict)
            entry = factory.load(index)
            assert entry == Sequence.from_dict(meta)


def test_bfile_loading():
    factory = make_factory()
    for key, sequence in factory.cache.items():
        assert not sequence.with_bfile
        data = list(oeis.bfile(key))
        if data:
            assert oeis.bfile_exists(key)
            assert sequence.sample <= data
            factory.load(key, with_bfile=True)
            assert data <= sequence.sample
            assert sequence.with_bfile
            sequence.sample_reset()
            assert sequence.sample <= data
        else:
            assert not oeis.bfile_exists(key)

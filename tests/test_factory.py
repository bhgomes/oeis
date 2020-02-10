# -*- coding: utf-8 -*- #
#
# tests/test_factory.py
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
Test OEIS Sequence Factory..

"""

# -------------- Standard Library -------------- #

# -------------- External Library -------------- #

import pytest
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.stateful import (
    RuleBasedStateMachine,
    rule,
    invariant,
    initialize,
    Bundle,
)

# ---------------- oeis Library ---------------- #

import oeis
from oeis.sequence import SequenceFactory, Registry
from .core import SESSION, random_ids, random_names


class FactoryMachine(RuleBasedStateMachine):

    meta_list = Bundle("meta_list")

    @initialize(cache=st.one_of(dict()), always_cache=st.booleans())
    def build_factory(self, cache, always_cache=False):
        # TODO: add more cache types
        self.factory = SequenceFactory.from_cache(
            cache, session=SESSION, always_cache=always_cache
        )
        self.registry = Registry.from_factory(self.factory)

    @rule(
        target=meta_list,
        key=st.one_of(random_ids(), random_names()),
        check_name=st.booleans(),
    )
    def load_meta(self, key, check_name):
        return self.factory.load_meta(key, check_name=check_name)

    @invariant()
    def caches_match(self):
        assert self.factory.cache == self.registry.cache


TestFactoryMachine = FactoryMachine.TestCase

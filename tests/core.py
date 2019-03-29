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
Test Sutie Core.

"""

# -------------- Standard Library -------------- #

from functools import partial

# -------------- External Library -------------- #

from numpy.random import randint

# ---------------- oeis Library ---------------- #

import oeis
from oeis.util import except_or, is_int


def random_id_gen(n, *, max_id=999999):
    """Get Generator to Random Potential OEIS Numbers."""

    def gen():
        return tuple(map(int, randint(max_id, size=n)))

    return gen


def random_oeis_sequences(n, *, max_id=999999, retries=10):
    """Download Random Sample Sequences from OEIS."""
    total = attempts = 0
    gen = random_id_gen(n, max_id=max_id)
    while total < n or attempts >= retries:
        for a in gen():
            seq = except_or(partial(oeis.A.load, a), Exception, None)
            if seq:
                total += 1
                yield seq
            if total == n:
                return
        attempts += 1

# -*- coding: utf-8 -*- #
#
# oeis/client.py
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
Client Interface to OEIS.

"""

# ---------------- oeis Library ---------------- #

from .base import name as oeis_name
from .util import import_package, getattrmethod, BoxObject, subset_box


__all__ = (
    "REQUESTS_SUPPORT",
    "REQUESTS_TOOLBELT_SUPPORT",
    "CACHE_CONTROL_SUPPORT",
    "AIOHTTP_SUPPORT",
    "QUERY_FORMAT",
    "ENTRY_FORMAT",
    "B_FILE_FORMAT",
    "fetch",
    "afetch",
    "query",
    "entry",
    "b_file",
)


requests, REQUESTS_SUPPORT = import_package("requests")


_, REQUESTS_TOOLBELT_SUPPORT = import_package("requests_toolbelt")


cachecontrol, CACHE_CONTROL_SUPPORT = import_package("cachecontrol")


aiohttp, AIOHTTP_SUPPORT = import_package("aiohttp")


QUERY_FORMAT = "https://oeis.org/search?q={0}&fmt=json"


ENTRY_FORMAT = "https://oeis.org/search?q=id:{0}&fmt=json"


B_FILE_FORMAT = "https://oeis.org/A{0}/b{0}.txt"


def get_text(response):
    """Get Text from Response."""
    return getattrmethod(response, "text", "")


def get_json(response):
    """Get JSON from Response."""
    return getattrmethod(response, "json", "")


def _fetch(url, session, *, as_json=True):
    """Fetch URL Content via Session."""
    with session.get(url) as response:
        return get_json(response) if as_json else get_text(response)


async def _afetch(url, session, *, as_json=True):
    """Asynchronously Fetch URL Content via Session."""
    async with session.get(url) as response:
        return await get_json(response) if as_json else get_text(response)


def _requests_fetch(url, session=requests, *args, **kwargs):
    """Default _requests_ Fetch."""
    return _fetch(url, session, *args, **kwargs)


class _aiohttp_mock_client_session:
    """Imitated _requests_ Get API."""

    async def get(*args, **kwargs):
        """Asynchronous Get."""
        async with aiohttp.ClientSession() as session:
            return await session.get(*args, **kwargs)


async def _aiohttp_afetch(url, session=_aiohttp_mock_client_session(), *args, **kwargs):
    """Default _aiohttp_ Asynchronous Fetch."""
    return await _afetch(url, session, *args, **kwargs)


fetch = _requests_fetch if REQUESTS_SUPPORT else _fetch


afetch = _aiohttp_afetch if AIOHTTP_SUPPORT else _afetch


def _fetch_formatted(url, value, *args, as_json=True, **kwargs):
    """Fetch Content from Formattd URL."""
    return fetch(url.format(value), *args, as_json=as_json, **kwargs)


async def _afetch_formatted(url, value, *args, as_json=True, **kwargs):
    """Asynchronously Fetch Content from Formattd URL."""
    return await afetch(url.format(value), *args, as_json=as_json, **kwargs)


def query(term, *args, **kwargs):
    """Search OEIS for Given Term."""
    if term:
        return _fetch_formatted(QUERY_FORMAT, term, *args, **kwargs)
    raise TypeError("Search Term must be non-empty.")


def entry(index, *args, check_name=True, **kwargs):
    """Get OEIS Entry Metadata."""
    if check_name:
        index = oeis_name(index)
    search_result = _fetch_formatted(ENTRY_FORMAT, index, *args, as_json=True, **kwargs)
    if not search_result["count"]:
        return BoxObject(None, raw=search_result)
    return subset_box(search_result, lambda d: d["results"][0], original="raw")


def b_file(index, *args, check_name=False, **kwargs):
    """Get B-File associated to OEIS Entry."""
    if check_name:
        index = oeis_name(index)
    pairs = (
        _fetch_formatted(B_FILE_FORMAT, index[1:], *args, as_json=False, **kwargs)
        .strip()
        .split()
    )
    return BoxObject(tuple(map(int, pairs[1::2])), offset=int(pairs[0]))

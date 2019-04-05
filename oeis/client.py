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

from wrapt import ObjectProxy

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
    "BFILE_FORMAT",
    "fetch",
    "afetch",
    "MISSING_PAGE_TEXT",
    "is_404",
    "FAILED_SEARCH_TEXT",
    "is_no_match",
    "query",
    "entry",
    "exists",
    "bfile",
    "bfile_exists",
    "Session",
)


requests, REQUESTS_SUPPORT = import_package("requests")


_, REQUESTS_TOOLBELT_SUPPORT = import_package("requests_toolbelt")


cachecontrol, CACHE_CONTROL_SUPPORT = import_package("cachecontrol")


aiohttp, AIOHTTP_SUPPORT = import_package("aiohttp")


QUERY_FORMAT = "https://oeis.org/search?q={0}&fmt=json"


ENTRY_FORMAT = "https://oeis.org/search?q=id:{0}&fmt=json"


BFILE_FORMAT = "https://oeis.org/A{0}/b{0}.txt"


def get_text(response):
    """
    Get Text from Response.

    :param response:
    :return:
    """
    return getattrmethod(response, "text", "")


def get_json(response):
    """
    Get JSON from Response.

    :param response:
    :return:
    """
    return getattrmethod(response, "json", "")


def _fetch(url, session, *, as_json=False):
    """
    Fetch URL Content via Session.

    :param url:
    :param session:
    :param as_json:
    :return:
    """
    with session.get(url) as response:
        return get_json(response) if as_json else get_text(response)


async def _afetch(url, session, *, as_json=False):
    """
    Asynchronously Fetch URL Content via Session.

    :param url:
    :param session:
    :param as_json:
    :return:
    """
    async with session.get(url) as response:
        return await get_json(response) if as_json else get_text(response)


def _requests_fetch(url, session=requests, *args, **kwargs):
    """
    Default _requests_ Fetch.

    :param url:
    :param session:
    :param args:
    :param kwargs:
    :return:
    """
    return _fetch(url, session, *args, **kwargs)


class _aiohttp_mock_client_session:
    """Imitated _requests_ Get API."""

    async def get(*args, **kwargs):
        """
        Asynchronous Get.

        :param args:
        :param kwargs:
        :return:
        """
        async with aiohttp.ClientSession() as session:
            return await session.get(*args, **kwargs)


async def _aiohttp_afetch(url, session=_aiohttp_mock_client_session(), *args, **kwargs):
    """
    Default _aiohttp_ Asynchronous Fetch.

    :param url:
    :param session:
    :param args:
    :param kwargs:
    :return:
    """
    return await _afetch(url, session, *args, **kwargs)


fetch = _requests_fetch if REQUESTS_SUPPORT else _fetch


afetch = _aiohttp_afetch if AIOHTTP_SUPPORT else _afetch


def _fetch_formatted(url, value, *args, as_json=False, **kwargs):
    """
    Fetch Content from Formatted URL.

    :param url:
    :param value:
    :param args:
    :param as_json:
    :param kwargs:
    :return:
    """
    return fetch(url.format(value), *args, as_json=as_json, **kwargs)


async def _afetch_formatted(url, value, *args, as_json=False, **kwargs):
    """
    Asynchronously Fetch Content from Formatted URL.

    :param url:
    :param value:
    :param args:
    :param as_json:
    :param kwargs:
    :return:
    """
    return await afetch(url.format(value), *args, as_json=as_json, **kwargs)


MISSING_PAGE_TEXT = (
    "Sorry, the page you requested was not found.",
    "Try the search box at the top of this page.",
)


def is_404(html):
    """
    Check if HTML from OEIS Website is the 404 Page.

    :param html:
    :return:
    """
    lines = iter(html.strip().split("\n"))
    try:
        for line in lines:
            if MISSING_PAGE_TEXT[0] in line:
                return MISSING_PAGE_TEXT[1] in next(lines)
    except StopIteration:
        pass
    return False


FAILED_SEARCH_TEXT = ("Sorry, but the terms do not match anything in the table.",)


def is_no_match(html):
    """
    Check if HTML from OEIS Website is the Missing Match Page.

    :param html:
    :return:
    """
    return any(FAILED_SEARCH_TEXT[0] in line for line in html.strip().split("\n"))


def query(term, *args, **kwargs):
    """
    Search OEIS for Given Term.

    :param term:
    :param args:
    :param kwargs:
    :return:
    """
    if term:
        return _fetch_formatted(QUERY_FORMAT, term, *args, **kwargs)
    raise TypeError("Search Term must be non-empty.")


def entry(number, *args, check_name=True, **kwargs):
    """
    Get OEIS Entry Metadata.

    :param number:
    :param args:
    :param check_name:
    :param kwargs:
    :return:
    """
    if check_name:
        number = oeis_name(number)
    result = _fetch_formatted(ENTRY_FORMAT, number, *args, as_json=True, **kwargs)
    if not result["count"]:
        return BoxObject(None, raw=result)
    return subset_box(result, key=lambda d: d["results"][0], origin_name="raw")


def exists(number, *args, **kwargs):
    """
    Check if Entry is Not None.

    :param number:
    :param args:
    :param kwargs:
    :return:
    """
    return bool(entry(number, *args, **kwargs))


def _get_bfile_line_content(line):
    """
    Get B-File Content without Comments.

    :param line:
    :return:
    """
    return line.partition("#")[0]


def _parsed_bfile_lines(lines):
    """
    Parse B-File Lines for Sequence.

    :param lines:
    :return:
    """
    lines = iter(lines)
    for line in lines:
        start = _get_bfile_line_content(line)
        if start:
            yield from map(int, start.split())
            break
    for line in lines:
        start = _get_bfile_line_content(line)
        if start:
            yield int(start.split()[1])


def bfile(number, *args, check_name=True, starting_index=0, **kwargs):
    """
    Get B-File associated to OEIS Entry.

    :param number:
    :param args:
    :param check_name:
    :param starting_index:
    :param kwargs:
    :return:
    """
    if check_name:
        number = oeis_name(number)
    html = _fetch_formatted(BFILE_FORMAT, number[1:], *args, **kwargs).strip()
    sequence = _parsed_bfile_lines(html.split("\n"))
    offset = 0
    try:
        offset = next(sequence)
        for _ in range(starting_index):
            next(sequence)
    except StopIteration:
        pass
    except Exception as error:
        if not is_404(html):
            raise error
    return BoxObject(tuple(sequence), offset=offset)


def bfile_exists(number, *args, **kwargs):
    """
    Check if B-File Exists for an OEIS Entry.

    :param number:
    :param args:
    :param kwargs:
    :return:
    """
    return bool(bfile(number, *args, **kwargs))


class Session(ObjectProxy):
    """Session Wrapper."""

    def __init__(self, session):
        """
        Initialize Session.

        :param session:
        """
        super().__init__(session)

    def fetch(self, url, *args, **kwargs):
        """
        Session fetch Wrapper.

        :param url:
        :param args:
        :param kwargs:
        :return:
        """
        return _fetch(url, self.__wrapped__, *args, **kwargs)

    def query(self, term, *args, **kwargs):
        """
        Session query Wrapper.

        :param term:
        :param args:
        :param kwargs:
        :return:
        """
        return query(term, self.__wrapped__, *args, **kwargs)

    def entry(self, number, *args, **kwargs):
        """
        Session entry Wrapper.

        :param number:
        :param args:
        :param kwargs:
        :return:
        """
        return entry(number, self.__wrapped__, *args, **kwargs)

    def exists(self, number, *args, **kwargs):
        """
        Session exists Wrapper.

        :param number:
        :param args:
        :param kwargs:
        :return:
        """
        return exists(number, self.__wrapped__, *args, **kwargs)

    def bfile(self, number, *args, **kwargs):
        """
        Session bfile Wrapper.

        :param number:
        :param args:
        :param kwargs:
        :return:
        """
        return bfile(number, self.__wrapped__, *args, **kwargs)

    def bfile_exists(self, number, *args, **kwargs):
        """
        Session bfile_exists Wrapper.

        :param number:
        :param args:
        :param kwargs:
        :return:
        """
        return bfile_exists(number, self.__wrapped__, *args, **kwargs)

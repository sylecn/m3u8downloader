#!/usr/bin/env python
# coding=utf-8

"""Project unit tests.

"""

from m3u8downloader.main import get_suffix_from_url


def test_dumb():
    """a unit test to make py.test run pass on empty project.

    """
    assert True


# test for get_suffix_from_url
def test_get_suffix_from_url():
    assert get_suffix_from_url("250kb/hls/index.m3u8") == ".m3u8"
    assert get_suffix_from_url("qpdL6296102.ts") == ".ts"
    assert get_suffix_from_url("qpdL6296102") == ""

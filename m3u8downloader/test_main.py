#!/usr/bin/env python
# coding=utf-8

"""Project unit tests.

"""

import os.path

from m3u8downloader.main import get_suffix_from_url
from m3u8downloader.main import is_higher_resolution
from m3u8downloader.main import get_url_path


# test for join
def test_join():
    assert os.path.normpath(os.path.join("/foo/bar/baz", "./abc.txt")) == "/foo/bar/baz/abc.txt"
    assert os.path.normpath(os.path.join(".", "./abc.txt")) == "abc.txt"


# test for get_url_path
def test_get_url_path():
    assert get_url_path('http://example.com/250kb/hls/index.m3u8') == '/250kb/hls/index.m3u8'
    assert get_url_path('http://example.com/index.m3u8') == '/index.m3u8'


# test for get_suffix_from_url
def test_get_suffix_from_url():
    assert get_suffix_from_url("250kb/hls/index.m3u8") == ".m3u8"
    assert get_suffix_from_url("qpdL6296102.ts") == ".ts"
    assert get_suffix_from_url("qpdL6296102") == ""


# test for is_higher_resolution
def test_is_higher_resolution():
    assert is_higher_resolution("480x854", None)
    assert not is_higher_resolution("480x854", "720x1280")
    assert is_higher_resolution("720x1280", "480x854")

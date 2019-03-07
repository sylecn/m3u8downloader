#!/usr/bin/env python
# coding=utf-8

"""Project unit tests.

"""

import os.path

from m3u8downloader.main import get_suffix_from_url
from m3u8downloader.main import is_higher_resolution
from m3u8downloader.main import get_url_path
from m3u8downloader.main import get_basename
from m3u8downloader.main import get_fullpath
from m3u8downloader.main import http_line_to_relpath_line


# test for http_line_to_relpath_line
def test_http_line_to_relpath_line():
    assert http_line_to_relpath_line("https://m3u.x8sinablog.net/20180627/1530068509/vts/audio000.png") == "20180627/1530068509/vts/audio000.png"
    assert http_line_to_relpath_line("https://m3u.x8sinablog.net/20180627/1530068509/vts/audio000.png?abc=def") == "20180627/1530068509/vts/audio000.png"
    assert http_line_to_relpath_line("hls-720p0.ts?e=1551942309&l=0&h=d7cf2b2173b6bfda5c9f738a8e39a7f6") == "hls-720p0.ts"


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


# test for get_basename
def test_get_basename():
    assert get_basename("foo.mp4") == "foo"
    assert get_basename("~/d/t2/foo.mp4") == "foo"
    assert get_basename("d/t2/foo.mp4") == "foo"
    assert get_basename("./foo.mp4") == "foo"
    assert get_basename("./foo") == "foo"


# test for get_fullpath
def test_get_fullpath():
    assert get_fullpath("foo") == os.path.abspath(os.path.join(os.curdir, "foo"))
    assert get_fullpath("foo/") == os.path.abspath(os.path.join(os.curdir, "foo"))
    assert get_fullpath("foo/bar") == os.path.abspath(os.path.join(os.curdir, "foo", "bar"))
    assert get_fullpath("~/foo/") == os.path.expanduser("~/foo")
    assert get_fullpath("$HOME/foo/") == os.path.expanduser("~/foo")

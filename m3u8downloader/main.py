#!/usr/bin/env python3
# coding=utf-8

"""download m3u8 file reliably.

Features:
- support HTTP and HTTPS proxy
- support retry on error/connect lost
- convert ts files to final mp4 file

"""

from __future__ import print_function, unicode_literals

import sys
import os
import os.path
import subprocess
import re
from urllib.parse import urljoin, urlparse
from collections import OrderedDict
import multiprocessing
import multiprocessing.queues
import logging

import requests
from wells.utils import retry

import m3u8downloader.configlogger    # pylint: disable=unused-import

logger = logging.getLogger(__name__)
SESSION = requests.Session()


def is_higher_resolution(new_resolution, old_resolution):
    """return True if new_resolution is higher than old_resolution.

    if old_resolution is None, just return True.

    resolution should be "1920x1080" format string.

    """
    if not old_resolution:
        return True
    return int(new_resolution.split("x")[0]) > int(old_resolution.split("x")[0])


def filesizeMiB(filename):
    s = os.stat(filename)
    return s.st_size / 1024 / 1024.0


def get_url_path(url):
    """get path part for a url.

    """
    return urlparse(url).path


def ensure_dir_exists_for(full_filename):
    """create file's parent dir if it doesn't exist.

    """
    os.makedirs(os.path.dirname(full_filename), exist_ok=True)


@retry(times=3, interval=[1, 5, 10])
def get_url_content(url):
    """fetch url, return content as bytes.

    """
    logger.debug("GET %s", url)
    r = SESSION.get(url)
    return r.content


def get_suffix_from_url(url):
    r = url.split(".")
    if len(r) == 1:
        return ""
    return "." + r[-1]


def get_basename(filename):
    """return filename with path and ext removed.

    """
    return os.path.splitext(os.path.basename(filename))[0]


def get_fullpath(filename):
    """make a canonical absolute path filename.

    """
    return os.path.abspath(os.path.expandvars(os.path.expanduser(filename)))


class M3u8Downloader:
    def __init__(self, url, output_filename, tempdir="."):
        self.start_url = url
        logger.info("output_filename=%s", output_filename)
        self.output_filename = get_fullpath(output_filename)
        self.tempdir = get_fullpath(
            os.path.join(tempdir, get_basename(output_filename)))
        try:
            os.makedirs(self.tempdir, exist_ok=True)
            logger.info("using temp dir at: %s", self.tempdir)
        except IOError as _:
            logger.exception("create tempdir failed for: %s", self.tempdir)
            raise

        self.media_playlist_localfile = None
        self.poolsize = 5
        # {full_url: local_file}
        self.fragments = OrderedDict()

    def start(self):
        self.download_m3u8_link(self.start_url)
        logger.info("%s fragments downloaded", len(self.fragments))
        target_mp4 = self.output_filename
        if not target_mp4.endswith(".mp4"):
            target_mp4 += ".mp4"
        cmd = ["ffmpeg", "-allowed_extensions", "ALL",
               "-i", self.media_playlist_localfile,
               "-acodec", "copy",
               "-vcodec", "copy",
               "-bsf:a", "aac_adtstoasc",
               target_mp4]
        logger.info("%s", cmd)
        proc = subprocess.run(cmd)
        if proc.returncode != 0:
            logger.error("run ffmpeg command failed: exitcode=%s",
                         proc.returncode)
            sys.exit(proc.returncode)
        logger.info("mp4 file created, size=%.1fMiB, filename=%s",
                    filesizeMiB(target_mp4), target_mp4)
        logger.info("Running: rm -rf \"%s\"", self.tempdir)
        subprocess.run(["/bin/rm", "-rf", self.tempdir])
        logger.info("temp files removed")

    def mirror_url_resource(self, remote_file_url):
        """download remote file and replicate the same dir structure locally.

        Return:
            local resource absolute path filename.

        """
        local_file = os.path.normpath(
            os.path.join(self.tempdir,
                         "." + get_url_path(remote_file_url)))
        if os.path.exists(local_file):
            logger.info("skip downloaded resource: %s", remote_file_url)
            return local_file
        content = get_url_content(remote_file_url)
        ensure_dir_exists_for(local_file)
        with open(local_file, 'wb') as f:
            f.write(content)
        return local_file

    def download_key(self, url, key_line):
        """download key.

        This will replicate key file in local dir.

        Args:
            key_line: a line looks like #EXT-X-KEY:METHOD=AES-128,URI="key.key"

        """
        pattern = re.compile(r'URI="([^"]+)"')
        mo = pattern.search(key_line)
        if not mo:
            raise RuntimeError("key line doesn't have URI")
        uri = mo.group(1)
        key_url = urljoin(url, uri)
        local_key_file = self.mirror_url_resource(key_url)
        logger.info("key downloaded at: %s", local_key_file)

    def download_fragment(self, url):
        """download a video fragment.

        """
        fragment_full_name = self.mirror_url_resource(url)
        if fragment_full_name:
            logger.info("fragment created at: %s", fragment_full_name)
        return (url, fragment_full_name)

    def fragment_downloaded(self, result):
        """apply_async callback.

        """
        url, fragment_full_name = result
        self.fragments[url] = fragment_full_name

    def fragment_download_failed(self, e):    # pylint: disable=no-self-use
        """apply_async error callback.

        """
        try:
            raise e
        except Exception:    # pylint: disable=broad-except
            # I don't have the url in the run time exception. hope requests
            # exception have it.
            logger.exception("fragment download failed")

    def download_fragments(self, fragment_urls):
        """download fragments.

        """
        pool = multiprocessing.Pool(self.poolsize)
        for url in fragment_urls:
            if url in self.fragments:
                logger.info("skip downloaded fragment: %s", url)
                continue
            pool.apply_async(self.download_fragment, (url,),
                             callback=self.fragment_downloaded,
                             error_callback=self.fragment_download_failed)
        pool.close()
        pool.join()

    def process_media_playlist(self, url, content=None):
        """replicate every file on the playlist in local temp dir.

        """
        self.media_playlist_localfile = self.mirror_url_resource(url)
        if content is None:
            content = get_url_content(url)

        fragment_urls = []
        for line in content.decode("utf-8").split('\n'):
            if line.startswith('#EXT-X-KEY'):
                self.download_key(url, line)
                continue
            if line.startswith('#') or line.strip() == '':
                continue
            if line.endswith(".m3u8"):
                raise RuntimeError("media playlist should not include .m3u8")
            fragment_urls.append(urljoin(url, line))

        self.download_fragments(fragment_urls)
        logger.info("media playlist all fragments downloaded")

    def process_master_playlist(self, url, content):
        """choose the highest quality media playlist, and download it.

        """
        last_resolution = None
        target_media_playlist = None
        replace_on_next_line = False
        pattern = re.compile(r'RESOLUTION=([0-9]+x[0-9]+)')
        for line in content.decode("utf-8").split('\n'):
            mo = pattern.search(line)
            if mo:
                resolution = mo.group(1)
                if is_higher_resolution(resolution, last_resolution):
                    last_resolution = resolution
                    replace_on_next_line = True
            if line.startswith('#'):
                continue
            if replace_on_next_line:
                target_media_playlist = line
                replace_on_next_line = False
            if target_media_playlist is None:
                target_media_playlist = line
        logger.info("choose resolution=%s uri=%s",
                    last_resolution, target_media_playlist)
        self.process_media_playlist(urljoin(url, target_media_playlist))

    def download_m3u8_link(self, url):
        """download video at m3u8 link.

        """
        content = get_url_content(url)
        if "RESOLUTION" in content.decode('utf-8'):
            self.process_master_playlist(url, content)
        else:
            self.process_media_playlist(url, content)


def main():
    try:
        ofile = sys.argv[1]
        url = sys.argv[2]
        if len(sys.argv) > 3:
            tempdir = sys.argv[3]
        else:
            tempdir = get_fullpath('~/.cache/m3u8downloader')
    except IndexError:
        logger.error("Usage: m3u8 OUTPUT_FILE URL")
        sys.exit(1)
    SESSION.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'})
    downloader = M3u8Downloader(url, ofile, tempdir)
    downloader.start()


if __name__ == '__main__':
    main()

#!/usr/bin/env python
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
from urllib.parse import urljoin
from collections import OrderedDict
import logging

import requests
from wells.utils import retry

import m3u8downloader.configlogger

logger = logging.getLogger(__name__)


@retry(times=3, interval=[1, 5, 10])
def get_url_content(url):
    logger.debug("GET %s", url)
    r = requests.get(url)
    return r.content


def get_suffix_from_url(url):
    r = url.split(".")
    if len(r) == 1:
        return ""
    return "." + r[-1]


class M3u8Downloader:
    def __init__(self, url, output_filename, tempdir="."):
        self.start_url = url
        self.output_filename = output_filename
        self.tempdir = os.path.abspath(
            os.path.join(tempdir, "tmp-" + output_filename))
        os.makedirs(self.tempdir, exist_ok=True)

        self.sequence_number = 0
        # {full_url: local_file}
        self.fragments = OrderedDict()

    def start(self):
        self.download_m3u8_link(self.start_url)
        logger.info("%s fragments downloaded", len(self.fragments))
        cmd = ["cat"]
        cmd.extend(self.fragments.values())
        combined_ts_file = os.path.join(self.tempdir, "all.ts")
        with open(combined_ts_file, "wb") as f:
            proc = subprocess.run(cmd, stdout=f)
            if proc.returncode != 0:
                logger.error("run cat command failed: exitcode=%s",
                             proc.returncode)
                sys.exit(proc.returncode)
            logger.info("combined ts file to %s", combined_ts_file)
        target_mp4 = self.output_filename
        if not target_mp4.endswith(".mp4"):
            target_mp4 += ".mp4"
        cmd = ["ffmpeg", "-i", combined_ts_file, "-acodec", "copy",
               "-vcodec", "copy", target_mp4]
        proc = subprocess.run(cmd)
        if proc.returncode != 0:
            logger.error("run ffmpeg command failed: exitcode=%s",
                         proc.returncode)
            sys.exit(proc.returncode)
        logger.info("mp4 file created: %s", target_mp4)
        if False:
            logger.info("clean up temp files")
            subprocess.run(["rm", "-rf", self.temp_dir])

    def next_fragment_name(self):
        result = "{:04d}".format(self.sequence_number)
        self.sequence_number += 1
        return result

    def download_fragment(self, url):
        """download a video fragment.

        """
        if url in self.fragments:
            logger.info("skip downloaded fragment: %s", url)
            return
        fragment_basename = self.next_fragment_name()
        fragment_suffix = get_suffix_from_url(url)
        fragment_full_name = os.path.join(self.tempdir,
                                          fragment_basename + fragment_suffix)
        if os.path.exists(fragment_full_name):
            logger.info("skip downloaded fragment: %s", url)
            return
        content = get_url_content(url)
        with open(fragment_full_name, "wb") as f:
            f.write(content)
        logger.info("created %s", fragment_full_name)
        self.fragments[url] = fragment_full_name

    def download_m3u8_link(self, url):
        """download video at m3u8 link.

        """
        content = get_url_content(url)
        for line in content.decode("utf-8").split('\n'):
            if line.startswith('#'):
                continue
            if line.endswith(".m3u8"):
                self.download_m3u8_link(urljoin(url, line))
            self.download_fragment(urljoin(url, line))


def main():
    try:
        ofile = sys.argv[1]
        url = sys.argv[2]
    except IndexError:
        logger.error("Usage: m3u8 OUTPUT_FILE URL")
        sys.exit(1)
    downloader = M3u8Downloader(url, ofile)
    downloader.start()


if __name__ == '__main__':
    main()

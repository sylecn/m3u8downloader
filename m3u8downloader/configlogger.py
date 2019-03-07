#!/usr/bin/env python2
# coding=utf-8

"""
config logger
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import os.path
import logging

from logging.config import fileConfig
from pkg_resources import resource_filename


def load_logger_config():
    """if /var/log/m3u8downloader exist, load default logger.conf.

    otherwise, try to create it directly.
    if that fails, try to create it with sudo.
    if that fails, use basic logger config.

    """
    logdir = "/var/log/m3u8downloader/"
    if os.path.exists(logdir):
        fileConfig(resource_filename("m3u8downloader", "logger.conf"))
        return

    ENV = os.getenv("ENV", "test")
    level = logging.INFO if ENV == "prod" else logging.DEBUG
    logging.basicConfig(
        format='%(asctime)s [%(name)s] %(levelname)-8s %(message)s',
        level=level)
    logging.info("Create log dir %s failed. Using basic config, level=%s",
                 logdir, level)


logging.captureWarnings(True)
load_logger_config()

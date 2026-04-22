# coding=utf-8

"""
config logger
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import os.path
import logging

from importlib import resources
from logging.config import fileConfig


def load_logger_config():
    """if /var/log/m3u8downloader exist, load default logger.conf.

    otherwise, try to create it directly.
    if that fails, try to create it with sudo.
    if that fails, use basic logger config.

    """
    logdir = "/var/log/m3u8downloader/"
    if os.path.exists(logdir):
        logger_conf = resources.files("m3u8downloader").joinpath("logger.conf")
        with resources.as_file(logger_conf) as logger_conf_path:
            fileConfig(str(logger_conf_path))
        return

    level = logging.INFO
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=level)
    logging.debug("log dir %s doesn't exist. Using basic config with level=%s",
                  logdir, level)


logging.captureWarnings(True)
load_logger_config()

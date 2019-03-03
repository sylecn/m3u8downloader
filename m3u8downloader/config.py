#!/usr/bin/env python2
# coding=utf-8

"""
config variables
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import logging
import os

from wells.config import ConfigurationManger

import m3u8downloader.configlogger    # pylint: disable=unused-import


logger = logging.getLogger(__name__)


TESTING = os.getenv("PYTEST") == "1"
DEBUGGING = os.getenv("DEBUG") == "1"

# set root logger level to ERROR when running unit test.
if TESTING:
    logging.getLogger('').setLevel(logging.ERROR)

DEFAULTS = {
    "host": "127.0.0.1",
    "port": "8082",
    "db.host": "localhost",
    "db.port": "5432",
    "db.name": "m3u8downloader",
    "db.user": "m3u8downloader",
    "db.password": "",
    "redis.host": "localhost",
    "redis.port": "6379",
    "redis.db": "0",
}

OPTIONAL_KEYS = list(DEFAULTS.keys())

REQUIRED_KEYS = [
]

CONF = ConfigurationManger(defaults=DEFAULTS,
                           configfiles=["/opt/m3u8downloader/conf/m3u8downloader.conf",
                                        "/etc/m3u8downloader.conf",
                                        "/etc/m3u8downloader/m3u8downloader.conf"],
                           required_keys=REQUIRED_KEYS,
                           optional_keys=OPTIONAL_KEYS)


def ensure_all_config_variable_defined():
    """check all config variable used in agent code is defined.

    exit with 0 on success, exit with non-zero on failure.

    """
    import sys
    import subprocess

    check_pass = True
    output = subprocess.check_output(r"""
rgrep 'CONF\.get' m3u8downloader/ |grep -o 'CONF\.get[a-z]\+("[^)]*")'|sed 's/.*("//; s/")//'
    """, shell=True).rstrip().decode("utf-8", 'ignore')
    all_keys = REQUIRED_KEYS + OPTIONAL_KEYS
    for line in output.split("\n"):
        if line and line not in all_keys:
            logger.error("undefined config variable: %s", line)
            check_pass = False
    sys.exit(0 if check_pass else 1)


def main():
    ensure_all_config_variable_defined()


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# coding=utf-8

"""
fabric file for server automation.
"""
# pylint: disable=line-too-long

import os.path
from fabric.api import env, sudo, run, local, hosts, put, cd

from utils.versionutils import get_version_from_init_file

env.use_ssh_config = True
PROD_HOST = 'de01'


@hosts(PROD_HOST)
def deploy():
    version = get_version_from_init_file()
    deb_file = "m3u8downloader_%s_amd64.deb" % (version,)
    if not os.path.exists(deb_file):
        local("make deb")
    put(deb_file)
    run("dpkg -i %s" % (deb_file,))

m3u8downloader
============================

m3u8downloader is a tool to download video at a m3u8 link. `HTTP Live
Streaming (HLS)`_ is becoming popular. m3u8 playlist is used by HLS to serve
video fragments of different quality to different clients. This tool supports
HLS master playlist and media playlist. If master playlist is given, it
selects the highest resolution automatically. HLS fragment encryption is
supported. Resume from partial download is supported, just rerun the same
command to continue.

ffmpeg is used to convert the downloaded fragments into final mp4 video file.

.. _HTTP Live Streaming (HLS): https://developer.apple.com/streaming/

Installation
------------

To install m3u8downloader, simply:

.. code-block:: bash

   $ sudo apt install -y ffmpeg pipx
   $ pipx install m3u8downloader


Quick Start
-----------

Example command line usage:

.. code-block:: bash

   downloadm3u8 -o ~/Downloads/foo.mp4 https://example.com/path/to/foo.m3u8

If ~/.local/bin is not in $PATH, you can use full path:

.. code-block:: bash

   ~/.local/bin/downloadm3u8 -o ~/Downloads/foo.mp4 https://example.com/path/to/foo.m3u8

Here is built-in command line help:

.. code-block:: bash

   usage: m3u8downloader [-h] [--user-agent USER_AGENT] [--origin ORIGIN] [--version]
                         [--debug] --output OUTPUT [--tempdir TEMPDIR] [--keep]
                         [--concurrency N]
                         URL
   
   download video at m3u8 url
   
   positional arguments:
     URL                   the m3u8 url
   
   optional arguments:
     -h, --help            show this help message and exit
     --user-agent USER_AGENT
                           specify User-Agent header for HTTP requests
     --origin ORIGIN       specify Origin header for HTTP requests
     --version             show program's version number and exit
     --debug               enable debug log
     --output OUTPUT, -o OUTPUT
                           output video filename, e.g. ~/Downloads/foo.mp4
     --tempdir TEMPDIR     temp dir, used to store .ts files before combing them into mp4
     --keep                keep files in tempdir after converting to mp4
     --concurrency N, -c N
                           number of fragments to download at a time

Documentation
-------------

Config File Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may use a config file to specify some command line arguments.

- supported config files, later takes precedence:

     - /etc/m3u8downloader.conf
     - /etc/m3u8downloader/m3u8downloader.conf
     - ~/.config/m3u8downloader.conf
     - ~/.config/m3u8downloader/m3u8downloader.conf

- config file format

  .. code-block:: bash

     # comments and empty lines are ignored.
     KEY=VALUE
     # or
     KEY="VALUE"
     # boolean values may be true|false|yes|no|1|0

- supported keys:

  .. code-block:: bash

     user_agent=<string>
     origin=<string>
     tempdir=<string>
     concurrency=<int>
     debug=<true|false>

  Their meaning is the same as their counterpart in command line arguments.

- if a config is specified both in config file and command line arguments,
  command line arguments will take precedence.

Limitations
-------------

This tool only parses minimum m3u8 extensions for selecting media playlist
from master playlist, downloading key and fragments from media playlist. If a
m3u8 file doesn't download correctly, it's probably some new extension was
added to the HLS spec which this tool isn't aware of.

Bug Report
------------

Bugs should be reported to `github issues`_.

.. _github issues: https://github.com/sylecn/m3u8downloader/issues

ChangeLog
---------

* v0.11.1

  - add --keep option to keep temp files after converting to mp4
  - bugfix: when on windows, properly delete temp dir when filename contains
    special characters.

* v0.10.1

  - lifted lib version restriction

* v0.10.0

  - add support for config file
  - handle Ctrl+C and SIGTERM properly

* v0.9.0

  - add support for --user-agent and --origin parameters

* v0.8.7

  - bugfix: do not rewrite KEY URI if it is already a local file path.

* v0.8.6

  - fix a regression in v0.8.4. the v0.8.4 release should be avoided. Either
    use v0.8.3 or v0.8.6+

* v0.8.4

  - minor bugfix: still try rewrite path when using m3u8 file from cache.
    when rewrite path in m3u8 file, do not rewrite if path has already been
    rewritten before. This is a minor change, it only fix things when process
    is killed when .m3u8 file is downloaded but path in it has not been
    rewritten yet.

* v0.8.3

  - bugfix: ensure output file name and temp dir name is always valid for
    windows platform.

* v0.8.1

  - bugfix: should rewrite key uri to local file path.
  - some bugfix for windows platform.

* v0.8.0 2019-03-31

  - add logrotate for log handler

* v0.7.8 2019-03-09

  - bugfix: fragment url rewrite fail for some cases

* v0.7.7 2019-03-08

  - bugfix: always rewrite fragment url to local abs path

* v0.7.5 2019-03-07

  - set default log level to INFO

* v0.7.4 2019-03-07

  - initial release

README for developers
==========================

How to add configurable variables
----------------------------------------

User configurations can be defined in m3u8downloader/config.py

Default config keys and values are defined in config.py. Runtime configs can
be read from config file or environment variable. Config file path is
specified in config.py.

Config file format is:

::

  # empty line and comment line are ignored
  key1=value1
  key2=value2

Every config key can be passed in as environment variable as well.  The
environment variable name is by replace . (dot) and - (hyphen-minus) by _
(underscore), then all upper case. For example, db.host env variable should be
DB_HOST. If the same key is defined in more than one place, env var > file
config > default config.

To use config variable in code,

.. code-block:: python

   from m3u8downloader.config import CONF

   CONF.getstr('some.key')
   CONF.getint('some.key')
   CONF.getbool('some.key')
   CONF.getfloat('some.key')


How to run tests and deploy projects
-----------------------------------------

- In dev environment,

  .. code-block:: bash

     make test
     make run

- In production, deploy via deb file,

  update scripts in deb-scripts/

  install fpm the package builder. see https://github.com/jordansissel/fpm
  install fabric tool. see http://www.fabfile.org/

  .. code-block:: bash

     make test
     make deb
     fab deploy

- In production, deploy via kubernetes and docker image.

  in Makefile, update DOCKER_IMAGE_PREFIX and BUILD_DOCKER_IMAGE if necessary,
  default template use my private docker reg.

  Run test in docker container and build docker image:

  define DOCKER_USER and DOCKER_PASSWORD env variable.

  .. code-block:: bash

     make ci-build

  Deploy in kubernetes cluster:

  define KUBECTL_API and KUBECTL_TOKEN env variable.

  .. code-block:: bash

     make deploy

  default template use ingress to provide https access to the service. In
  other environment, the app.yaml template should be updated to fit in the
  environment.

How to add git commit hooks etc
---------------------------------

Using git pre-commit hook is a good idea.

.. code-block:: bash

   make install-git-hooks

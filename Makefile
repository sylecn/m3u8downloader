PYTHON_MODULES := m3u8downloader
PYTHONPATH := .
VENV := .venv
PYTEST := env PYTHONPATH=$(PYTHONPATH) PYTEST=1 $(VENV)/bin/py.test
PYLINT := env PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/pylint --disable=I0011,line-too-long,invalid-name --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"
PEP8 := env PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/pycodestyle --repeat --ignore=E202,E501,E402,W504
PYTHON := env PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/python
PIP := $(VENV)/bin/pip

DEFAULT_PYTHON ?= $(shell ./utils/choose_default_python.sh)
VIRTUALENV := $(wildcard ./utils/virtualenv-*/virtualenv.py)

REQUIREMENTS := -r requirements.txt
DEV_REQUIREMENTS := -r requirements-dev.txt

VERSION := $(shell grep '__version__' m3u8downloader/__init__.py |cut -d'"' -f 2)
# docker hub user name or private registry URL with username.
DOCKER_IMAGE_PREFIX := de02-reg.emacsos.com/sylecn

BUILD_DOCKER_IMAGE := de02-reg.emacsos.com/sylecn/python-build-image:1.0.0

default: check-coding-style
dist: bootstrap
	rm -rf dist/*
	$(PYTHON) setup.py -q sdist
	$(PYTHON) setup.py -q bdist_wheel --universal
upload: dist
	test -e $(VENV)/bin/twine || $(PIP) install -q twine
	$(VENV)/bin/twine check dist/*.whl
	$(VENV)/bin/twine check dist/*.tar.gz
	$(VENV)/bin/twine upload dist/*
build:

version:
	@echo $(VERSION)
debug:
	env DEBUG=1 $(PYTHON) m3u8downloader/main.py
run:
	$(PYTHON) m3u8downloader/main.py -o $(OFILE) $(URL)
uwsgi:
	$(VENV)/bin/uwsgi --processes=2 --threads=4 --wsgi-file=m3u8downloader/main.py --env=PYTHONPATH=. --http=localhost:8082 --disable-logging
shell:
	$(PYTHON) -i

venv:
	test -d $(VENV) || $(DEFAULT_PYTHON) $(VIRTUALENV) --no-download -q $(VENV)
requirements:
	@if [ -d wheelhouse ]; then \
		$(PIP) install -q --isolated --no-index --find-links=wheelhouse $(REQUIREMENTS); \
	else \
		$(PIP) install -q $(REQUIREMENTS); \
	fi
logdir:
	@if [ ! -d /var/log/m3u8downloader ]; then \
		sudo mkdir /var/log/m3u8downloader; \
		sudo chown -R ${USER} /var/log/m3u8downloader; \
	fi
bootstrap: venv requirements
bootstrap-dev: REQUIREMENTS += $(DEV_REQUIREMENTS)
bootstrap-dev: venv requirements
install: bootstrap
	$(PIP) install -q --no-index .
uninstall: bootstrap
	$(PIP) uninstall -q -y m3u8downloader
docker: deb
	docker build -t $(DOCKER_IMAGE_PREFIX)/m3u8downloader:$(VERSION) .
	@echo "You may push it with: docker push $(DOCKER_IMAGE_PREFIX)/m3u8downloader:$(VERSION)"
deb:
	utils/build-deb
pipfreeze:
	$(PIP) freeze
wheel: bootstrap-dev
	@echo "building wheelhouse..."
	$(PIP) install wheel
	$(PIP) wheel -w wheelhouse $(REQUIREMENTS)

check: just-test
sanity-check: bootstrap
	$(PYTHON) m3u8downloader/sanity_check.py
check-coding-style: bootstrap-dev
	$(PEP8) $(PYTHON_MODULES)
	$(PYLINT) -E $(PYTHON_MODULES)
pylint-full: check-coding-style
	$(PYLINT) $(PYTHON_MODULES)
test: check-coding-style
	$(PYTEST) $(PYTHON_MODULES)
just-test:
	$(PYTEST) $(PYTHON_MODULES)

# run test, build deb in python build image container, then create docker
# image and push image on host.
ci-build:
	docker login -u $(DOCKER_USER) -p $(DOCKER_PASSWORD) $(BUILD_DOCKER_IMAGE)
	docker run --rm --name m3u8downloader-test -v "$(CURDIR)":/app -u $(shell id -u):$(shell id -g) $(BUILD_DOCKER_IMAGE) make test deb -C /app
	docker build -t $(DOCKER_IMAGE_PREFIX)/m3u8downloader:$(VERSION) .
	docker push $(DOCKER_IMAGE_PREFIX)/m3u8downloader:$(VERSION)
deploy:
	sed "s/IMAGE_TAG/$(VERSION)/" app.yaml > $(VERSION).yaml
	kubectl --certificate-authority=/etc/kubernetes/pki/ca.crt -s $(KUBECTL_API) --token=$(KUBECTL_TOKEN) apply -f $(VERSION).yaml

install-dev-no-wheel:
	$(PIP) install -q -i https://pypi.tuna.tsinghua.edu.cn/simple $(DEV_REQUIREMENTS)
test-prod: install-dev-no-wheel test

clean:
	find . -name "__pycache__" -type d -exec rm -rf {} \; || true
	find . -name "*.pyc" -type f -exec rm -rf {} \; || true
full-clean:
	rm -rf $(VENV) build/ dist/ wheelhouse/ m3u8downloader.egg-info/ distribute-*.tar.gz
	find . -name "__pycache__" -type d -exec rm -rf {} \; || true
	find . -name "*.pyc" -type f -exec rm -rf {} \; || true
todo:
	@rgrep -I -n --exclude=Makefile --exclude=TAGS --exclude-dir=$(VENV) -E '(TODO|FIXME|XXX|not_implemented)' $(PYTHON_MODULES)
TAGS:
	etags -R --exclude=static $(PYTHON_MODULES)
update-git-hooks: install-git-hooks-force
install-git-hooks:
	./utils/install-git-hooks
install-git-hooks-force:
	./utils/install-git-hooks -f
loc:
	find . -regex '.*\.pyw?$$' -exec wc -l {} \+ | tail -n 1
	which cloc >/dev/null && cloc m3u8downloader/
.PHONY: default build debug run uwsgi shell venv bootstrap bootstrap-dev install uninstall deb pipfreeze wheel check check-coding-style pylint-full test just-test test-prod clean full-clean todo TAGS update-git-hooks install-git-hooks install-git-hooks-force loc

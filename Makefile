SHELL ?= /bin/bash
TIMESTAMP ?= $(shell date +"%Y%m%d-%H%M")

MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
MAKEFILE_DIR := $(dir $(MAKEFILE_PATH))
HOME_PATH ?= $(MAKEFILE_DIR)
ENV_NAME ?= _env
ENV_PATH ?= $(abspath $(HOME_PATH)/$(ENV_NAME))

PYTHON_GLOBAL ?= python3
PIP = '$(ENV_PATH)/bin/pip'
PYTHON = '$(ENV_PATH)/bin/python'
UVICORN = '$(ENV_PATH)/bin/uvicorn'
PYTEST = '$(ENV_PATH)/bin/pytest'

DOCKER_BIN ?= docker


tea: env clean build lint tests start


env:
	$(PYTHON_GLOBAL) -m venv "$(ENV_PATH)"
	$(PIP) install --upgrade --requirement '$(HOME_PATH)mapas/back/requirements.txt'


start:
	cd mapas/back/; \
	MAPA_SERVE_STATIC="$(HOME_PATH)/mapas/front/www/" \
	MAPA_DATABASE_URL="$${MAPA_DATABASE_URL:-sqlite:///$(HOME_PATH)/db.sqlite}" \
	$(PYTHON) ./main.py


lint:
	'$(ENV_PATH)/bin/pylint' mapas/back/
	'$(ENV_PATH)/bin/flake8' mapas/back/


build: build_front clean


build_front:
	cd '$(HOME_PATH)mapas/front/'; \
	make build EXPANDER='$(ENV_PATH)/bin/expander.py -f'


demodb:
	cd mapas/back/; \
	MAPA_DATABASE_URL='sqlite:///$(HOME_PATH)/db.sqlite' \
	$(PYTHON) ../tools/demodb.py

citydb: GEONAMES_SOURCE ?= https://download.geonames.org/export/dump/cities15000.zip
citydb: GEONAMES_FILEZIP ?= "$(HOME_PATH)/_data/cities15000.zip"
citydb: GEONAMES_FILE ?= "$(HOME_PATH)/_data/cities15000.txt"
citydb: GEONAMES_COUNTRY_SOURCE ?= https://download.geonames.org/export/dump/countryInfo.txt
citydb: GEONAMES_COUNTRY_FILE ?= "$(HOME_PATH)/_data/countryInfo.txt"
citydb:
	@echo "Download files from geonames.org …"
	mkdir -pv `dirname "$(GEONAMES_FILEZIP)" "$(GEONAMES_COUNTRY_FILE)"`
	wget -c "$(GEONAMES_SOURCE)" -O "$(GEONAMES_FILEZIP)"
	unzip -o "$(GEONAMES_FILEZIP)" -d `dirname "$(GEONAMES_FILE)"`
	wget -c "$(GEONAMES_COUNTRY_SOURCE)" -O "$(GEONAMES_COUNTRY_FILE)"
	ls -l $(GEONAMES_COUNTRY_FILE) $(GEONAMES_FILE)

	cd mapas/back/; \
	MAPA_DATABASE_URL='sqlite:///$(HOME_PATH)/db.sqlite' \
	$(PYTHON) ../tools/citydb.py "$(GEONAMES_FILE)" "$(GEONAMES_COUNTRY_FILE)"


container_build:
	"$(DOCKER_BIN)" build \
	--file mapas.Dockerfile \
	--tag mapas \
	--force-rm \
	"$(HOME_PATH)"


container_run: container_stop
	"$(DOCKER_BIN)" run \
	--publish 8000:8000 \
	--tty --interactive \
	--rm --replace \
	--name mapas \
	mapas


container_stop:
	-"$(DOCKER_BIN)" stop -t 1 mapas


tests:
	cd mapas/back/; \
	MAPA_DATABASE_URL='sqlite:///:memory:' \
	$(PYTEST) -v -s --cache-clear .


clean:
	find '$(HOME_PATH)mapas/back/' -iname '*.pyc' -print -delete
	find '$(HOME_PATH)mapas/back/' -iname __pycache__ -print -delete

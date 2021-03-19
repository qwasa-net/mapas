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

DOCKER ?= docker
CONNAME ?= mapas

DEPLOY_HOST ?= mapas.tktk.in
DEPLOY_PATH ?= /home/mapas.tktk.in/

.PHONY: help

help:
	-@grep -E "^[a-z_0-9]+:" "$(strip $(MAKEFILE_LIST))" | grep '##' | sed 's/:.*##\s*/ —— /ig'

tea: clean env build lint tests demodb start  ## build and start


env:  ## install python runtime environment
	$(PYTHON_GLOBAL) -m venv "$(ENV_PATH)"
	$(PIP) install --upgrade --requirement '$(HOME_PATH)mapas/back/requirements.txt'

start:  ## start local demo server ($MAPA_LISTEN_HOST:$MAPA_LISTEN_PORT, default 127.0.0.1:8000)
	cd mapas/back/; \
	MAPA_SERVE_STATIC="$(HOME_PATH)/mapas/front/www/" \
	MAPA_DATABASE_URL="$${MAPA_DATABASE_URL:-sqlite:///$(HOME_PATH)/db.sqlite}" \
	$(PYTHON) ./main.py

build: build_front clean  ## build

build_front:
	cd '$(HOME_PATH)mapas/front/'; \
	make \
	--directory='$(HOME_PATH)mapas/front/' \
	--file='$(HOME_PATH)mapas/front/Makefile' \
	install_tools build \
	EXPANDER='$(ENV_PATH)/bin/expander.py -f'

lint:  ## run backend linters
	'$(ENV_PATH)/bin/pylint' mapas/back/
	'$(ENV_PATH)/bin/flake8' mapas/back/

tests:  ## run backend tests
	cd mapas/back/; \
	MAPA_DATABASE_URL='sqlite:///:memory:' \
	$(PYTEST) -v -s --cache-clear .

clean:  ## clear python cache
	-find '$(HOME_PATH)mapas/back/' -iname '*.pyc' -print -delete
	-find '$(HOME_PATH)mapas/back/' -iname __pycache__ -print -delete
	-find '$(HOME_PATH)mapas/back/' -ipath '*/\.pytest_cache/*' -print -delete

testdb:  ## create test database
	cd mapas/back/; \
	MAPA_DATABASE_URL='sqlite:///$(HOME_PATH)/db.sqlite' \
	$(PYTHON) ../tools/demodb.py

demodb:  ## create demo database (cities)
	cp -v demodb.sqlite db.sqlite

citydb: GEONAMES_SOURCE ?= https://download.geonames.org/export/dump/cities15000.zip
citydb: GEONAMES_FILEZIP ?= "$(HOME_PATH)/_data/cities15000.zip"
citydb: GEONAMES_FILE ?= "$(HOME_PATH)/_data/cities15000.txt"
citydb: GEONAMES_COUNTRY_SOURCE ?= https://download.geonames.org/export/dump/countryInfo.txt
citydb: GEONAMES_COUNTRY_FILE ?= "$(HOME_PATH)/_data/countryInfo.txt"
citydb:  ## download (from geonames), parse and generate cities database
	@echo "Download files from geonames.org …"
	mkdir -pv `dirname "$(GEONAMES_FILEZIP)" "$(GEONAMES_COUNTRY_FILE)"`
	wget -c "$(GEONAMES_SOURCE)" -O "$(GEONAMES_FILEZIP)"
	unzip -o "$(GEONAMES_FILEZIP)" -d `dirname "$(GEONAMES_FILE)"`
	wget -c "$(GEONAMES_COUNTRY_SOURCE)" -O "$(GEONAMES_COUNTRY_FILE)"
	ls -l $(GEONAMES_COUNTRY_FILE) $(GEONAMES_FILE)

	cd mapas/back/; \
	MAPA_DATABASE_URL='sqlite:///$(HOME_PATH)/db.sqlite' \
	$(PYTHON) "$(HOME_PATH)/tools/citydb.py" "$(GEONAMES_FILE)" "$(GEONAMES_COUNTRY_FILE)"


#
### containers
container_build:  ## build container
	"$(DOCKER)" build \
	--file mapas.Dockerfile \
	--tag "$(CONNAME)" \
	--force-rm \
	"$(HOME_PATH)"

container_run: container_stop  ## run container (local)
	"$(DOCKER)" run \
	--publish 8000:8000 \
	--tty --interactive \
	--rm --replace \
	--name "$(CONNAME)" \
	"$(CONNAME)"

container_stop:  ## stop container (local)
	-"$(DOCKER)" stop -t 1 "$(CONNAME)"

#
### deploy to mapas.tktk.in
deploy_copy_files: clean ## copy files (to deploy host)
	ssh $(DEPLOY_HOST) 'mkdir -p "$(DEPLOY_PATH)" "$(DEPLOY_PATH)/logs"'
	-rsync --recursive --verbose \
	--exclude  "node_modules" \
	"$(HOME_PATH)/deploy" "$(HOME_PATH)/mapas" "$(HOME_PATH)/Makefile" \
	"$(DEPLOY_HOST):$(DEPLOY_PATH)/"

deploy_load_image: container_build ## load container (at deploy host)
	$(DOCKER) save "$(CONNAME)" | ssh $(DEPLOY_HOST) $(DOCKER) load

deploy_create_container: deploy_stop_container ## create container from loaded/pulled image (at deploy host)
	ssh $(DEPLOY_HOST) '$(DOCKER) create \
	--name "$(CONNAME)" \
	--replace=true \
	--restart=on-failure:10 \
	--publish 127.0.0.1:8090:8000 \
	"$(CONNAME)"'

deploy_stop_container:
	-@ssh $(DEPLOY_HOST) '$(DOCKER) container stop -t 1 $(CONNAME); $(DOCKER) container rm $(CONNAME)'

deploy_install: ## setup nginx proxy and systemd service (at deploy host)
	ssh $(DEPLOY_HOST) sudo \
	"ln -sf $(DEPLOY_PATH)/deploy/nginx.conf /etc/nginx/sites-enabled/mapas.tktk.in.conf; \
	systemctl reload nginx; \
	cp $(DEPLOY_PATH)/deploy/logrotate.conf /etc/logrotate.d/mapas.tktk.in; \
	systemctl link --force $(DEPLOY_PATH)/deploy/systemd-podman-mapas.service; \
	systemctl daemon-reload; \
	systemctl stop systemd-podman-mapas.service; sleep 2; \
	systemctl start systemd-podman-mapas.service"

deploy_restart:
	ssh $(DEPLOY_HOST) sudo \
	"systemctl reload nginx; \
	systemctl daemon-reload; \
	systemctl stop systemd-podman-mapas.service; sleep 2; \
	systemctl start systemd-podman-mapas.service"

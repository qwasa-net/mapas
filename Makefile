SHELL ?= /bin/bash
TIMESTAMP ?= $(shell date +"%Y%m%d-%H%M")

MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
MAKEFILE_DIR := $(dir $(MAKEFILE_PATH))
HOME_PATH ?= $(MAKEFILE_DIR)
ENV_NAME ?= _env
ENV_PATH ?= $(abspath $(HOME_PATH)/$(ENV_NAME))

PYTHON_GLOBAL = python3
PIP = '$(ENV_PATH)/bin/pip'
PYTHON = '$(ENV_PATH)/bin/python'
UVICORN = '$(ENV_PATH)/bin/uvicorn'


tea: env clean build lint tests start


env:
	$(PYTHON_GLOBAL) -m venv "$(ENV_PATH)"
	$(PIP) install --upgrade --requirement '$(HOME_PATH)mapas/back/requirements.txt'


start:
	cd mapas/back/;\
	MAPA_SERVE_STATIC='$(HOME_PATH)/mapas/front/src/' \
	$(PYTHON) ./main.py


lint:
	'$(ENV_PATH)/bin/pylint' mapas/back/
	'$(ENV_PATH)/bin/flake8' mapas/back/


build:
	#


demodb:
	#


tests:
	#


clean:
	find '$(HOME_PATH)mapas/back/' -iname '*.pyc' -print -delete
	find '$(HOME_PATH)mapas/back/' -iname __pycache__ -print -delete

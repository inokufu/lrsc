ifeq (, $(shell which docker 2>/dev/null))
  $(error "No docker found in PATH!")
endif

include .env

DOCKER_COMPOSE_AVAILABLE := $(shell docker compose version >/dev/null 2>&1 && echo yes || echo no)

ifeq ($(DOCKER_COMPOSE_AVAILABLE),yes)
  COMPOSE_CMD = docker compose
else
  COMPOSE_CMD = docker-compose
endif

PROJECT_NAME = learninglocker

ENV ?= dev

COMPOSE_FILES = -f docker-compose.yml -f docker-compose.$(ENV).yml

.PHONY: build up down logs

GLOBAL_COMPOSE_CMD = $(COMPOSE_CMD) $(COMPOSE_FILES)
GLOBAL_COMPOSE_CMD_UP = $(GLOBAL_COMPOSE_CMD) up -d

build:
	$(GLOBAL_COMPOSE_CMD) build

up:
	$(GLOBAL_COMPOSE_CMD_UP)

down:
	$(GLOBAL_COMPOSE_CMD) down

logs:
	$(GLOBAL_COMPOSE_CMD) logs -f

build-up:
	$(GLOBAL_COMPOSE_CMD_UP) --build

create-site-admin:
	$(GLOBAL_COMPOSE_CMD) exec api node cli/dist/server createSiteAdmin ${MASTER_EMAIL} ${ORGANIZATION_NAME} ${MASTER_PASSWORD}

disable-register:
	$(GLOBAL_COMPOSE_CMD) exec api node cli/dist/server disableRegister

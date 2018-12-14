.PHONY: build

SHELL := /bin/bash

build: ## Build the project
        docker build -t dshelper .

runlinux: ## Run the project in Linux
        xhost local:root
        docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$$DISPLAY dshelper
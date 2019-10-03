#!/bin/bash
# Installs software for tools.

TOOLS=$(dirname ${BASH_SOURCE[0]})
LOG_NAME=setup_tools
source ${TOOLS}/common.sh

log "Installing APT packages."
apt-get -qq update
apt-get -qq install -y \
    parallel \
    protobuf-compiler \
    python-virtualenv \
    python3-pip

log "Building tools virtualenv."
(cd ${TOOLS} && \
    virtualenv -p /usr/bin/python3 venv && \
    source venv/bin/activate && \
    pip install -U -r requirements.txt && \
    deactivate)

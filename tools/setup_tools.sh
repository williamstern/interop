#!/bin/bash
# Installs software for tools.

TOOLS=$(readlink -f $(dirname ${BASH_SOURCE[0]}))
LOG_NAME=setup_tools
source ${TOOLS}/common.sh

log "Installing APT packages."
apt-get -qq update
apt-get -qq install -y \
    graphviz \
    parallel \
    postgresql-client \
    protobuf-compiler \
    python-virtualenv \
    python3-matplotlib \
    python3-nose \
    python3-numpy \
    python3-pip \
    python3-psycopg2 \
    python3-pyproj \
    python3-scipy

log "Building tools virtualenv."
(cd ${TOOLS} && \
    virtualenv -p /usr/bin/python3 ${TOOLS}/venv && \
    source ${TOOLS}/venv/bin/activate && \
    pip install -U -r requirements.txt && \
    deactivate)

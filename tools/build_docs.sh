#!/bin/bash
# Build the documentation.

set -e
TOOLS=$(readlink -f $(dirname ${BASH_SOURCE[0]}))
DOCS=${TOOLS}/../docs
SERVER=${TOOLS}/../server

source ${TOOLS}/venv/bin/activate
make -C ${DOCS} SPHINXOPTS=-W html

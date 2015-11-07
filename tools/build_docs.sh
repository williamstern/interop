#!/bin/bash

set -e

# This directory
tools=$(readlink -f $(dirname ${BASH_SOURCE[0]}))
# Base repo directory
repo=$(readlink -f ${tools}/..)

source ${repo}/docs/venv/bin/activate

# Build HTML, treating warnings as errors.
make -C ${repo}/docs SPHINXOPTS=-W html

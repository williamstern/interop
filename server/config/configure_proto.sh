#!/bin/bash
# Compiles the proto definitions.

CONFIG=$(readlink -f $(dirname ${BASH_SOURCE[0]}))
PROTO=auvsi_suas/proto
set -e

(cd ${CONFIG}/.. && protoc --python_out=. ${PROTO}/*.proto)

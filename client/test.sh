#!/bin/bash
# Tests the Interop Client Docker image.

set -e
CLIENT=$(readlink -f $(dirname ${BASH_SOURCE[0]}))

docker run --net="host" -it auvsisuas/interop-client bash -c \
    "export PYTHONPATH=/interop/client && \
     cd /interop/client && \
     source venv2/bin/activate && \
     python /usr/bin/nosetests auvsi_suas.client && \
     deactivate && \
     source venv3/bin/activate && \
     python /usr/bin/nosetests auvsi_suas.client && \
     deactivate && \
     source venv2/bin/activate && \
     python /usr/bin/nosetests tools && \
     deactivate && \
     source venv3/bin/activate && \
     python /usr/bin/nosetests tools && \
     deactivate"

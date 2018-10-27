#!/bin/bash
# Tests the Interop Client Docker image.

set -e
CLIENT=$(readlink -f $(dirname ${BASH_SOURCE[0]}))

# Test install with setuptools.
(cd ${CLIENT} &&
 virtualenv --system-site-packages -p /usr/bin/python2 test-venv2 && \
 source test-venv2/bin/activate && \
 python setup.py install && \
 python setup.py test && \
 python setup.py clean && \
 deactivate)
(cd ${CLIENT} &&
 virtualenv --system-site-packages -p /usr/bin/python3 test-venv3 && \
 source test-venv3/bin/activate && \
 python3 setup.py install && \
 python3 setup.py test && \
 python3 setup.py clean && \
 deactivate)

# Test the containers.
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

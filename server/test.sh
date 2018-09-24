#!/bin/bash
# Tests the Interop Server Docker image.

docker run -it auvsisuas/interop-server bash -c \
    "sudo service postgresql start && \
     sudo service memcached start && \
     cd /interop/server && \
     python3 manage.py test"

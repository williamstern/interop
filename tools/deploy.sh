#!/bin/bash
# Deploys Docker containers to hub.

set -e
TOOLS=$(readlink -f $(dirname ${BASH_SOURCE[0]}))
source ${SETUP}/common.sh


log "Tagging Docker images."
DATE=$(date '+%Y.%m')
docker tag auvsisuas/interop-client:latest auvsisuas/interop-client:${DATE}
docker tag auvsisuas/interop-server:latest auvsisuas/interop-server:${DATE}

log "Logging into Docker."
docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD"

log "Pushing Docker images."
docker push auvsisuas/interop-server
docker push auvsisuas/interop-client

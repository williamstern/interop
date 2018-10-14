#!/bin/bash
# Builds the Interop Client Docker image.

CLIENT=$(readlink -f $(dirname ${BASH_SOURCE[0]}))
REPO=${CLIENT}/..
docker build -t auvsisuas/interop-client ${REPO} -f ${CLIENT}/Dockerfile

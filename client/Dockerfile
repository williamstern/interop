FROM ubuntu:18.04
WORKDIR /interop/client

# Set the time zone to the competition time zone.
RUN ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime

RUN apt-get -qq update && apt-get -qq install -y \
        libxml2-dev \
        libxslt-dev \
        protobuf-compiler \
        python \
        python-dev \
        python-lxml \
        python-nose \
        python-pip \
        python-pyproj \
        python-virtualenv \
        python3 \
        python3-dev \
        python3-nose \
        python3-pip \
        python3-pyproj \
        python3-lxml \
        sudo

COPY client/requirements.txt requirements.txt
RUN bash -c "virtualenv --system-site-packages -p /usr/bin/python2 \
            /interop/client/venv2 && \
        source /interop/client/venv2/bin/activate && \
        pip install -r requirements.txt && \
        deactivate" && \
    bash -c "virtualenv --system-site-packages -p /usr/bin/python3 \
            /interop/client/venv3 && \
        source /interop/client/venv3/bin/activate && \
        pip3 install -r requirements.txt && \
        deactivate"

COPY client/ .

COPY proto auvsi_suas/proto
RUN protoc --python_out=. auvsi_suas/proto/*.proto

CMD bash --init-file configure.sh

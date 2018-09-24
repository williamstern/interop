FROM ubuntu:18.04
WORKDIR /interop/server

# Set the time zone to the competition time zone.
RUN ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime

# Install server base dependencies.
RUN apt-get -qq update && apt-get -qq install -y \
        apache2 \
        apache2-utils \
        curl \
        libapache2-mod-auth-pgsql \
        libapache2-mod-auth-plain \
        libapache2-mod-python \
        libapache2-mod-wsgi-py3 \
        libapache2-mod-xsendfile \
        memcached \
        postgresql \
        postgresql-client \
        protobuf-compiler \
        python3 \
        # Install from apt as it's much faster.
        python3-matplotlib \
        python3-numpy \
        python3-pip \
        python3-psycopg2 \
        python3-pyproj \
        python3-scipy \
        sudo

# Install server Python requirements.
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Configure database & web server.
COPY manage.py manage.py
COPY server server
COPY auvsi_suas/__init__.py auvsi_suas/__init__.py
COPY auvsi_suas/models/__init__.py auvsi_suas/models/__init__.py
COPY auvsi_suas/views/__init__.py auvsi_suas/views/__init__.py
COPY auvsi_suas/views/auvsi_admin/__init__.py auvsi_suas/views/auvsi_admin/__init__.py
COPY auvsi_suas/migrations auvsi_suas/migrations
COPY config config
COPY fixtures fixtures
RUN ./config/configure_postgresql.sh && \
    ./config/configure_apache.sh && \
    python3 manage.py collectstatic --noinput

# Compile protobuf definitions.
COPY auvsi_suas/proto auvsi_suas/proto
RUN ./config/configure_proto.sh

# Copy remaining code.
COPY . .

# Load initial data.
RUN service postgresql start && \
    ./healthcheck.py --check_postgres && \
    python3 manage.py migrate && \
    python3 manage.py loaddata fixtures/test_fixture.yaml

# Host-mountable sections.
VOLUME /var/log/apache2 /var/lib/postgresql /var/www/media/objects

# On run: start database, cache, server, and don't exit.
CMD service postgresql start && \
  service memcached start && \
  service apache2 start && \
  tail -f /dev/null

HEALTHCHECK \
  CMD ./healthcheck.py --check_postgres --check_apache --check_homepage

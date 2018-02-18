FROM ubuntu:16.04
WORKDIR /interop/server

# Install server base dependencies.
RUN apt-get -qq update && apt-get -qq install -y \
        apache2 \
        apache2-utils \
        curl \
        libapache2-mod-auth-pgsql \
        libapache2-mod-auth-plain \
        libapache2-mod-python \
        libapache2-mod-wsgi \
        libapache2-mod-xsendfile \
        memcached \
        nodejs \
        npm \
        postgresql \
        postgresql-client \
        protobuf-compiler \
        python \
        # Install from apt as it's much faster.
        python-matplotlib \
        python-numpy \
        python-pip \
        python-psycopg2 \
        python-pyproj \
        python-scipy \
        sudo

# Install server Javascript requirements.
RUN ln -snf /usr/bin/nodejs /usr/local/bin/node && \
    npm install -g \
        jasmine-core \
        karma \
        karma-chrome-launcher \
        karma-jasmine \
        karma-phantomjs-launcher \
        phantomjs

# Install server Python requirements.
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Configure database, web server, Django.
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
    ./config/configure_django.sh

# Compile protobuf definitions.
COPY auvsi_suas/proto auvsi_suas/proto
RUN ./config/configure_proto.sh

# Copy remaining code.
COPY . .

# Load initial data.
RUN service postgresql start && \
    ./healthcheck.py --check_postgres && \
    python manage.py loaddata fixtures/test_fixture.yaml

# Host-mountable sections.
VOLUME /var/log/apache2 /var/lib/postgresql

# On run: start database, cache, server, and don't exit.
CMD service postgresql start && \
  service memcached start && \
  service apache2 start && \
  tail -f /dev/null

HEALTHCHECK \
  CMD ./healthcheck.py --check_postgres --check_apache --check_homepage

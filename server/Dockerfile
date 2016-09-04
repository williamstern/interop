FROM ubuntu:14.04
WORKDIR /interop/server

RUN sudo apt-get -qq update && sudo apt-get -qq install -y \
        apache2 \
        apache2-utils \
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
        python \
        # Install from apt as it's much faster.
        python-matplotlib \
        python-numpy \
        python-pip \
        python-psycopg2 \
        python-pyproj \
        python-scipy

RUN sudo ln -snf /usr/bin/nodejs /usr/local/bin/node && \
    sudo npm install -g \
        karma \
        karma-chrome-launcher \
        karma-jasmine \
        karma-phantomjs-launcher \
        phantomjs

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY config config
RUN ./config/configure_postgresql.sh && \
    ./config/configure_apache.sh

COPY . .
RUN ./config/configure_django.sh

VOLUME /var/log/apache2 /var/lib/postgresql/9.3/data

CMD sudo service postgresql start && \
  sudo service memcached start && \
  sudo service apache2 start && \
  tail -f /dev/null

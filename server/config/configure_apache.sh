#!/bin/bash
# Configures the apache server.

CONFIG=$(readlink -f $(dirname ${BASH_SOURCE[0]}))

set -e

chown -R www-data /var/www
cp ${CONFIG}/xsendfile.conf /etc/apache2/conf-enabled/
cp ${CONFIG}/limit_upload.conf /etc/apache2/conf-enabled/
cp ${CONFIG}/interop_apache.conf /etc/apache2/sites-enabled/
cp ${CONFIG}/apache2.conf /etc/apache2/
a2dismod python
service apache2 restart

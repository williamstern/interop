# This script launches the Puppet automated dependency installer.
# ==============================================================================

# Quit immediately on any error
set -e

# Create soft link from repo to standardize scripts
if [ -h /auvsi_suas_competition ]
then
    sudo rm /auvsi_suas_competition;
fi
sudo ln -s ${PWD}/.. /auvsi_suas_competition

# Update the package list
sudo apt-get -y update

# Upgrade old packages
sudo apt-get -y upgrade

# Install Puppet
sudo apt-get -y install puppet

# Install puppet modules
sudo mkdir -p /etc/puppet/modules/
sudo puppet module install -f puppetlabs/stdlib
sudo puppet module install -f puppetlabs-apt
sudo puppet module install -f puppetlabs-apache
sudo puppet module install -f puppetlabs-concat
sudo puppet module install -f puppetlabs-mysql
sudo puppet module install -f puppetlabs-ntp

# Launch the Puppet process. Installs dependencies and configures Apache.
sudo puppet apply --modulepath=${PWD}/puppet_files:/etc/puppet/modules/:/usr/share/puppet/modules/ puppet_files/auvsi_suas.pp

# Create the database with a test admin
# (username: testadmin, password: testpass)
(
cd ../src/auvsi_suas_server;
if [ ! -d data ]
then
    mkdir data;
fi
if [ -f data/db.sqlite3 ]
then 
    sudo mv data/db.sqlite3 "data/db.sqlite3.`date`";
fi
sudo python manage.py syncdb --noinput;
sudo chown www-data:www-data data;
sudo chown www-data:www-data data/db.sqlite3;
)

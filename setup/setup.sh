# This script launches the Puppet automated dependency installer.
# ==============================================================================

C='\033[0;32m'
NC='\033[0m'

# Quit immediately on any error
set -e

# Create soft link from repo to standardize scripts
printf "${C}Creating softlinks...${NC}\n"
if [ -h /auvsi_suas_competition ]
then
    sudo rm /auvsi_suas_competition;
fi
sudo ln -s ${PWD}/.. /auvsi_suas_competition

# Update the package list
printf "${C}Updating package list and upgrading packages...${NC}\n"
sudo apt-get -y update
# Upgrade old packages
sudo apt-get -y upgrade

# Install Puppet
printf "${C}Installing Puppet and modules...${NC}\n"
sudo apt-get -y install puppet
# Install puppet modules
sudo mkdir -p /etc/puppet/modules/
sudo puppet module install -f puppetlabs/stdlib
sudo puppet module install -f puppetlabs-apt
sudo puppet module install -f puppetlabs-apache
sudo puppet module install -f puppetlabs-concat
sudo puppet module install -f puppetlabs-mysql
sudo puppet module install -f puppetlabs-ntp
sudo puppet module install -f puppetlabs-postgresql
sudo puppet module install -f stankevich-python

# Launch the Puppet process. Installs dependencies and configures Apache.
printf "${C}Executing Puppet setup...${NC}\n"
sudo puppet apply --modulepath=${PWD}/puppet_files:/etc/puppet/modules/:/usr/share/puppet/modules/ puppet_files/auvsi_suas.pp

# Create the database with a test admin
# (username: testadmin, password: testpass)
printf "${C}Creating data folder & setting up database...${NC}\n"
(
cd ../src/auvsi_suas_server;
if [ ! -d data ]
then
    mkdir data;
fi
python manage.py migrate auth;
python manage.py migrate sessions;
python manage.py migrate admin;
python manage.py migrate;
python manage.py syncdb --noinput;
)

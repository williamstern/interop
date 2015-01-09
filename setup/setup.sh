# This script launches the Puppet automated dependency installer.
# ==============================================================================

# Quit immediately on any error
set -e

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

# Launch the Puppet process
sudo puppet apply --modulepath=${PWD}/puppet_files:/etc/puppet/modules/:/usr/share/puppet/modules/ puppet_files/auvsi_suas.pp

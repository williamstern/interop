# This script initializes the system so that automated setup can prepare the
# system for development and deployment.
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
sudo puppet module install -f puppetlabs-apt

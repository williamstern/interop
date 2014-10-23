# This script launches the Puppet automated dependency installer. The init.sh
# script should be executed prior to running this script. 
# ==============================================================================

set -e

# Install puppet modules
sudo mkdir -p /etc/puppet/modules/
sudo puppet module install puppetlabs-apt

# Launch the Puppet process
sudo puppet apply --modulepath=${PWD}/puppet_files:/etc/puppet/modules/:/usr/share/puppet/modules/ puppet_files/auvsi_suas.pp

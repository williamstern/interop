# This script launches the Puppet automated dependency installer. The setup.sh
# script should be executed prior to running this script. 
# ==============================================================================

# Launch the Puppet process
puppet apply --modulepath=${PWD}/puppet_files puppet_files/auvsi_suas.pp

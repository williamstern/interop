# AUVSI SUAS Puppet Module: base
# Base, core system setup
# ==============================================================================

class auvsi_suas::base {
    # Install python and pip
    class { 'python' :
        version => 'system',
        pip     => true,
    }
}

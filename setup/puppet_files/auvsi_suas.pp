# AUVSI SUAS Puppet Setup Script
# This file launches the module install after configuring the path
# ==============================================================================

Exec {
    path => ["/bin",
             "/sbin",
             "/usr/bin",
             "/usr/sbin"],
    logoutput => true,
}

include auvsi_suas

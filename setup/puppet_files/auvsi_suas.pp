# AUVSI SUAS Puppet Setup Script
# This file launches the module install after configuring the path
# ==============================================================================

# Configure system so it can begin setup
Exec {
    # Configure the path for execution
    path => ["/bin",
             "/sbin",
             "/usr/bin",
             "/usr/sbin"],
    # Log output for setup
    logoutput => true,
}

# Run apt update before anything else
exec { "apt-update":
    command => "/usr/bin/apt-get update"
}

Exec["apt-update"] -> Package <| |>

# Execute puppet setup for AUVSI SUAS
include auvsi_suas

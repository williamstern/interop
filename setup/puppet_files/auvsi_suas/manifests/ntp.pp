# AUVSI SUAS Puppet Module: ntp
# ==============================================================================

# ntp module definition
class auvsi_suas::ntp {

    # Package list
    $package_deps = ["ntp"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


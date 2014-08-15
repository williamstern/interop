# AUVSI SUAS Puppet Module: gcc
# ==============================================================================

# gcc module definition
class auvsi_suas::gcc {

    # Package list
    $package_deps = ["gcc"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


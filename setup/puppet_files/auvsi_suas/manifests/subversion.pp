# AUVSI SUAS Puppet Module: subversion
# ==============================================================================

# subversion module definition
class auvsi_suas::subversion {

    # Package list
    $package_deps = ["subversion"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


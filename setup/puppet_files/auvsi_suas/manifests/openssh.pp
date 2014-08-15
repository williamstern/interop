# AUVSI SUAS Puppet Module: openssh
# ==============================================================================

# openssh module definition
class auvsi_suas::openssh {

    # Package list
    $package_deps = ["openssh-client",
                     "openssh-server"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


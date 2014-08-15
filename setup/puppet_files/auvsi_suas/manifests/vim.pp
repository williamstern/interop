# AUVSI SUAS Puppet Module: vim
# ==============================================================================

# vim module definition
class auvsi_suas::vim {

    # Package list
    $package_deps = ["vim"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


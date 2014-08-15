# AUVSI SUAS Puppet Module: dia
# ==============================================================================

# dia module definition
class auvsi_suas::dia {

    # Package list
    $package_deps = ["dia"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


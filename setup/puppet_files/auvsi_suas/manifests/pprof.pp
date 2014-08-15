# AUVSI SUAS Puppet Module: pprof
# ==============================================================================

# pprof module definition
class auvsi_suas::pprof {

    # Package list
    $package_deps = ["google-perftools"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


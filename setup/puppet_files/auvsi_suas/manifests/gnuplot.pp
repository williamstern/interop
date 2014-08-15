# AUVSI SUAS Puppet Module: gnuplot
# ==============================================================================

# gnuplot module definition
class auvsi_suas::gnuplot {

    # Package list
    $package_deps = ["gnuplot"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


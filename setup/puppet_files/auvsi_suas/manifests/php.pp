# AUVSI SUAS Puppet Module: php
# ==============================================================================

# php module definition
class auvsi_suas::php {

    # Package list
    $package_deps = ["php5"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


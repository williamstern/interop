# AUVSI SUAS Puppet Module: rsync
# ==============================================================================

# rsync module definition
class auvsi_suas::rsync {

    # Package list
    $package_deps = ["rsync"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


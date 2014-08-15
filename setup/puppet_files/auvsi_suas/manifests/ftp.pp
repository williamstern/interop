# AUVSI SUAS Puppet Module: ftp
# ==============================================================================

# ftp module definition
class auvsi_suas::ftp {

    # Package list
    $package_deps = ["ftp",
                     "ftpd"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


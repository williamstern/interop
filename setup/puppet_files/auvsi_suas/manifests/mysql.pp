# AUVSI SUAS Puppet Module: mysql
# ==============================================================================

# mysql module definition
class auvsi_suas::mysql {

    # Package list
    $package_deps = ["mysql-client",
                     "mysql-server"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


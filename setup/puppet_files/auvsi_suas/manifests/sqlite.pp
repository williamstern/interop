# AUVSI SUAS Puppet Module: sqlite
# ==============================================================================

# sqlite module definition
class auvsi_suas::sqlite {

    # Package list
    $package_deps = ["sqlite3"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


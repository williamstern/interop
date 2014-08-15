# AUVSI SUAS Puppet Module: openssl
# ==============================================================================

# openssl module definition
class auvsi_suas::openssl {

    # Prerequisite modules
    require auvsi_suas::python
    
    # Package list
    $package_deps = ["openssl",
                     "python-openssl",
                     "python3-openssl"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


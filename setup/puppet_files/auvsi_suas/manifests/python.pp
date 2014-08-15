# AUVSI SUAS Puppet Module: python
# ==============================================================================

# python module definition
class auvsi_suas::python {

    # Package list
    $package_deps = ["python",
                     "python3"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


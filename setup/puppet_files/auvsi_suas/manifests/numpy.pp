# AUVSI SUAS Puppet Module: numpy
# ==============================================================================

# numpy module definition
class auvsi_suas::numpy {

    # Prerequisite modules
    require auvsi_suas::python

    # Package list
    $package_deps = ["python-numpy",
                     "python3-numpy",
                     "python-scipy",
                     "python3-scipy"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


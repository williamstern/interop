# AUVSI SUAS Puppet Module: matplotlib
# ==============================================================================

# matplotlib module definition
class auvsi_suas::matplotlib {

    # Prerequisite modules
    require auvsi_suas::numpy
    require auvsi_suas::python
    
    # Package list
    $package_deps = ["python-matplotlib",
                     "python3-matplotlib"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


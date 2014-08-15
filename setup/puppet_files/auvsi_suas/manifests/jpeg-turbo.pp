# AUVSI SUAS Puppet Module: jpeg-turbo
# ==============================================================================

# jpeg-turbo module definition
class auvsi_suas::jpeg-turbo {

    # Package list
    $package_deps = ["libjpeg-turbo8",
                     "libjpeg-turbo8-dev"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


# AUVSI SUAS Puppet Module: imagemagick
# ==============================================================================

# imagemagick module definition
class auvsi_suas::imagemagick {

    # Package list
    $package_deps = ["imagemagick"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


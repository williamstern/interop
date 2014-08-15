# AUVSI SUAS Puppet Module: grahpicsmagick
# ==============================================================================

# grahpicsmagick module definition
class auvsi_suas::graphicsmagick {

    # Package list
    $package_deps = ["graphicsmagick"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


# AUVSI SUAS Puppet Module: cmake
# ==============================================================================

# cmake module definition
class auvsi_suas::cmake {

    # Prerequisite modules
    require auvsi_suas::boost
    require auvsi_suas::gcc
    require auvsi_suas::opencv
    require auvsi_suas::pprof
    require auvsi_suas::protobuf
    require auvsi_suas::python
    require auvsi_suas::qt
    require auvsi_suas::sqlite
    require auvsi_suas::texlive

    # Package list
    $package_deps = ["cmake",
                     "cmake-curses-gui",
                     "cmake-qt-gui"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


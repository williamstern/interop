# AUVSI SUAS Puppet Module: eclipse
# ==============================================================================

# eclipse module definition
class auvsi_suas::eclipse {

    # Prerequisite modules
    require auvsi_suas::cmake
    require auvsi_suas::django
    require auvsi_suas::gcc
    require auvsi_suas::git
    require auvsi_suas::java
    require auvsi_suas::numpy
    require auvsi_suas::php
    require auvsi_suas::python
    require auvsi_suas::subversion
    require auvsi_suas::texlive
    require auvsi_suas::vim

    # Package list
    $package_deps = ["eclipse",
                     "eclipse-cdt",
                     "eclipse-cdt-autotools",
                     "eclipse-cdt-jni",
                     "eclipse-cdt-qt",
                     "eclipse-cdt-valgrind",
                     "eclipse-cdt-valgrind-remote"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}



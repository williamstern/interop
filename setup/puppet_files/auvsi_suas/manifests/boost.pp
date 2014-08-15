# AUVSI SUAS Puppet Module: boost
# ==============================================================================

# boost Module definition
class auvsi_suas::boost {

    # Prerequisite modules
    require auvsi_suas::gcc
    require auvsi_suas::numpy
    require auvsi_suas::python

    # Package list
    $package_deps = ["libboost-chrono-dev",
                     "libboost-date-time-dev",
                     "libboost-dev",
                     "libboost-doc",
                     "libboost-filesystem-dev",
                     "libboost-iostreams-dev",
                     "libboost-program-options-dev",
                     "libboost-python-dev",
                     "libboost-regex-dev",
                     "libboost-serialization-dev",
                     "libboost-system-dev",
                     "libboost-test-dev",
                     "libboost-thread-dev",
                     "libboost-all-dev",
                     "libboost-atomic-dev",
                     "libboost-context-dev",
                     "libboost-coroutine-dev",
                     "libboost-exception-dev",
                     "libboost-graph-dev",
                     "libboost-graph-parallel-dev",
                     "libboost-locale-dev",
                     "libboost-log-dev",
                     "libboost-math-dev",
                     "libboost-mpi-dev",
                     "libboost-mpi-python-dev",
                     "libboost-random-dev",
                     "libboost-signals-dev",
                     "libboost-timer-dev",
                     "libboost-tools-dev",
                     "libboost-wave-dev"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


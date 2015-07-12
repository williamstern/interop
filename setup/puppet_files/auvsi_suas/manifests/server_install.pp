# AUVSI SUAS Puppet Module: server_install
# Installs suas server, plus dependencies
# ==============================================================================

class auvsi_suas::server_install {
    require auvsi_suas::base

    # Install some packages from apt, since they are slow/tricky to build.
    $package_deps = [
        "python-numpy",
        "python-scipy",
        "python-matplotlib",
        "python-psycopg2",
    ]
    package { $package_deps:
        ensure => "latest",
    }

    python::requirements { '/interop/server/requirements.txt' :
    }
}

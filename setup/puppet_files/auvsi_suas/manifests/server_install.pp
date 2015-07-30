# AUVSI SUAS Puppet Module: server_install
# Installs suas server, plus dependencies
# ==============================================================================

class auvsi_suas::server_install {
    require auvsi_suas::base

    # Install packages from apt.
    $package_deps = [
        "python-numpy",
        "python-scipy",
        "python-matplotlib",
        "python-psycopg2",
        "npm",
    ]
    package { $package_deps:
        ensure => "latest",
    }

    # Install python server requirements.
    python::requirements { '/interop/server/requirements.txt' :
    }

    # Install packages from NPM.
    exec { 'npm install karma and jasmine':
        command => "npm install -g karma karma-jasmine karma-chrome-launcher karma-cli",
        cwd => "/interop/server",
        require => Package['npm'],
    }
}

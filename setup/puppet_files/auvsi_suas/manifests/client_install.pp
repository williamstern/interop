# AUVSI SUAS Puppet Module: client_install
# Installs interop client library twice. Once in a Python 2 virtualenv, once in
# a Python 3 virtualenv.
# ==============================================================================

class auvsi_suas::client_install {
    require auvsi_suas::base

    # Python 2 virtualenv
    python::virtualenv { '/interop/client/new/venv2' :
        ensure => 'present',
        version => 'system',
        requirements => '/interop/client/new/requirements.txt',
    }

    # Python 3 virtualenv
    python::virtualenv { '/interop/client/new/venv3' :
        ensure => 'present',
        version => '3.4',
        requirements => '/interop/client/new/requirements.txt',
    }

    # We install in 'develop' mode, so changes to the source file
    # are immediately reflected when running.

    # Install in Python 2 virtualenv
    python::pip { 'interop2' :
        pkgname => '/interop/client/new',
        ensure => 'latest',
        virtualenv => '/interop/client/new/venv2',
        install_args => ['-e'], # develop mode
        require => Python::Virtualenv['/interop/client/new/venv2'],
    }

    # Install in Python 3 virtualenv
    python::pip { 'interop3' :
        pkgname => '/interop/client/new',
        ensure => 'latest',
        virtualenv => '/interop/client/new/venv3',
        install_args => ['-e'], # develop mode
        require => Python::Virtualenv['/interop/client/new/venv3'],
    }

    # Install nose for testing
    python::pip { 'nose2' :
        pkgname => 'nose',
        ensure => 'latest',
        virtualenv => '/interop/client/new/venv2',
        require => Python::Virtualenv['/interop/client/new/venv2'],
    }
    python::pip { 'nose3' :
        pkgname => 'nose',
        ensure => 'latest',
        virtualenv => '/interop/client/new/venv3',
        require => Python::Virtualenv['/interop/client/new/venv3'],
    }
}

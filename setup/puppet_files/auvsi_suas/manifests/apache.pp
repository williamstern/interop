# AUVSI SUAS Puppet Module: apache
# ==============================================================================

# apache module definition
class auvsi_suas::apache {

    # Prerequisite modules
    require auvsi_suas::apt_sources # libapache2-mod-fastcgi needs multiverse
    require auvsi_suas::gcc
    require auvsi_suas::java
    require auvsi_suas::mysql
    require auvsi_suas::openssh
    require auvsi_suas::openssl
    require auvsi_suas::php
    require auvsi_suas::python
    require auvsi_suas::sqlite

    # Package list
    $package_deps = ["apache2",
                     "apache2-utils",
                     "libapache2-mod-apparmor",
                     "libapache2-mod-auth-mysql",
                     "libapache2-mod-auth-pgsql",
                     "libapache2-mod-auth-plain",
                     "libapache2-mod-php5",
                     "libapache2-mod-python",
                     "libapache2-mod-wsgi",
                     "libapache2-mod-fastcgi",
                     "puppet-module-puppetlabs-apache"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


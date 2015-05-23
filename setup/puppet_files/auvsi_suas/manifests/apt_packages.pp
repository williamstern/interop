# AUVSI SUAS Puppet Module: apt_packages
# Installs all aptitude packages for various dependencies
# ==============================================================================

# Aptitude package module definition
class auvsi_suas::apt_packages {

    # Require aptitude sources
    require auvsi_suas::apt_sources

    # Package list
    $package_deps = [
        # General
        "ntp",
        "ftp",
        "ftpd",
        "openssh-client",
        "openssh-server",
        "openssl",
        "rsync",
        "vim",
        # Database
        "sqlite3",
        "python-mysqldb",
        # Source control
        "git",
        # Apache
        "apache2-utils",
        "libapache2-mod-auth-mysql",
        "libapache2-mod-auth-pgsql",
        "libapache2-mod-auth-plain",
        "libapache2-mod-python",
        "libapache2-mod-wsgi",
    ]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}

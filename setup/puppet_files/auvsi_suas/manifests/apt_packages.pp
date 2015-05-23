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
        # Languages
        "python",
        # Database
        "sqlite3",
        "python-mysqldb",
        "python-psycopg2",
        # Source control
        "git",
        # Apache
        "apache2-utils",
        "libapache2-mod-auth-mysql",
        "libapache2-mod-auth-pgsql",
        "libapache2-mod-auth-plain",
        "libapache2-mod-python",
        "libapache2-mod-wsgi",
        # General Python packages
        "python-pip",
        "python-numpy",
        "python-scipy",
        "python-openssl",
        "python-matplotlib",
        # Django
        "python-django",
        "python-django-auth-ldap",
        "python-django-auth-openid",
        "python-django-debug-toolbar",
        "python-django-extensions",
        "python-django-extra-views",
        "python-django-filter",
        "python-django-filters",
        "python-django-lint",
        "python-django-model-utils",
        "python-django-notification",
        "python-django-oauth-plus",
        "python-django-openid-auth",
        "python-django-pagination",
        "python-django-pipeline",
        "python-django-ratelimit",
        "python-django-shorturls",
        "python-django-shortuuidfield",
        "python-django-websocket",
    ]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}

# AUVSI SUAS Puppet Module: postgresql_config
# Configures the Postgres server.
# ==============================================================================

# postgresql_config module definition
class auvsi_suas::postgresql_config {
    # Need postgres installed
    require auvsi_suas::apt_packages

    # Setup postgresql server
    class { 'postgresql::server':
        postgres_password => 'postgresql_pass',
    }

    # Create superuser role
    postgresql::server::role { 'postgresql_user':
        password_hash => postgresql_password('postgresql_user', 'postgresql_pass'),
        superuser => true
    }

    # Create database for competition server
    postgresql::server::db { 'auvsi_suas_db':
        user => 'postgresql_user',
        password => postgresql_password('postgresql_user', 'postgresql_pass'),
    }
}

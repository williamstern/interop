# AUVSI SUAS Puppet Module: mysql_config
# Configures the MySQL server.
# ==============================================================================

# mysql_config module definition
class auvsi_suas::mysql_config {
    # Need mysql installed
    require auvsi_suas::apt_packages

    # Configure base server
    class { '::mysql::server':
        root_password => 'testpass',
        remove_default_accounts => true,
        override_options => $override_options
    }

    # Configure the database
    mysql::db { 'auvsi_suas_db':
        user => 'mysql_user',
        password => 'mysql_pass',
        host => 'localhost',
        grant => ['CREATE', 'INSERT', 'SELECT', 'ALTER', 'UPDATE', 'DELETE'],
    }
}

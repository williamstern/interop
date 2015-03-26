# AUVSI SUAS Puppet Module: apache_config
# Configures Apache server to use WSGI and point at auvsi_suas server.
# ==============================================================================

# apache_config module definition
class auvsi_suas::apache_config {
    # Need apache installed
    require auvsi_suas::apt_packages

    # Configure apache defaults
    class { 'apache':
      default_vhost => false,
    }
    # Configure the python path
    class { 'apache::mod::wsgi':
      wsgi_python_path   => '/auvsi_suas_competition/src/auvsi_suas_server/',
    }
    # Configure production via WSGI
    apache::vhost { 'auvsi_suas_server':
      port => '80',
      docroot => '/var/www/',
      wsgi_application_group => '%{GLOBAL}',
      wsgi_daemon_process => 'wsgi',
      wsgi_daemon_process_options => {
        processes => '2',
        threads => '6',
        display-name => '%{GROUP}',
      },
      wsgi_import_script => '/auvsi_suas_competition/src/auvsi_suas_server/auvsi_suas_server/wsgi.py',
      wsgi_import_script_options  =>
        { process-group => 'wsgi', application-group => '%{GLOBAL}' },
      wsgi_process_group => 'wsgi',
      wsgi_script_aliases => { 
        '/' => '/auvsi_suas_competition/src/auvsi_suas_server/auvsi_suas_server/wsgi.py'
      },
      error_log_file => 'auvsi_suas_server.debug.log',
      aliases => [
        { alias => '/static/admin',
          path => '/usr/lib/python2.7/dist-packages/django/contrib/admin/static/admin/',
        },
      ],
    }
}

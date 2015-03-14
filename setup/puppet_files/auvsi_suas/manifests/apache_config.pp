# AUVSI SUAS Puppet Module: apache_config
# Configures Apache server to use WSGI and point at auvsi_suas server.
# ==============================================================================

include apache

# apache_config module definition
class auvsi_suas::apache_config {
    # Need apache installed
    require auvsi_suas::apt_packages
   
    # Configure production performance via WSGI on port 80 
    # TODO
}

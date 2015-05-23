# AUVSI SUAS Setup Script
# This file launches the install for the various required components
# =============================================================================

# Create the main AUVSI SUAS definition. Including this definition will
# setup all system dependencies.
class auvsi_suas {
    include auvsi_suas::apt_sources
    include auvsi_suas::base
    include auvsi_suas::server_setup
    include auvsi_suas::apache_setup
    include auvsi_suas::postgresql_setup
}

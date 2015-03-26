# AUVSI SUAS Setup Script
# This file launches the install for the various required components
# =============================================================================

# Create the main AUVSI SUAS definition. Including this definition will
# setup all system dependencies.
class auvsi_suas {
    include auvsi_suas::apt_packages
    include auvsi_suas::apache_config
    include auvsi_suas::postgresql_config
}

# AUVSI SUAS Pet Setup Script
# This file launches the install for the various required components
# =============================================================================

# Create the main AUVSI SUAS pet definition. Including this definition will
# setup all system dependencies.
class auvsi_suas {
    # System Dependencies
    include auvsi_suas::apache
    include auvsi_suas::apt_sources
    include auvsi_suas::chrome
    include auvsi_suas::django
    include auvsi_suas::eclipse
    include auvsi_suas::ftp
    include auvsi_suas::gcc
    include auvsi_suas::git
    include auvsi_suas::gnuplot
    include auvsi_suas::graphicsmagick
    include auvsi_suas::imagemagick
    include auvsi_suas::java
    include auvsi_suas::jpeg-turbo
    include auvsi_suas::matplotlib
    include auvsi_suas::mysql
    include auvsi_suas::ntp
    include auvsi_suas::numpy
    include auvsi_suas::opencv
    include auvsi_suas::openssh
    include auvsi_suas::openssl
    include auvsi_suas::pprof
    include auvsi_suas::protobuf
    include auvsi_suas::python
    include auvsi_suas::rsync
    include auvsi_suas::sqlite
    include auvsi_suas::vim
}

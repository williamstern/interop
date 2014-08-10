# AUVSI SUAS Puppet Setup Script
# This file launches the install for the various required components
# =============================================================================

class auvsi_suas {
    # System Dependencies
    include auvsi_suas::apache.pp
    include auvsi_suas::apt.pp
    include auvsi_suas::boost.pp
    include auvsi_suas::chrome.pp
    include auvsi_suas::cmake.pp
    include auvsi_suas::django.pp
    include auvsi_suas::eclipse.pp
    include auvsi_suas::ftp.pp
    include auvsi_suas::gcc.pp
    include auvsi_suas::git.pp
    include auvsi_suas::gnuplot.pp
    include auvsi_suas::graphicsmagick.pp
    include auvsi_suas::imagemagick.pp
    include auvsi_suas::init.pp
    include auvsi_suas::java.pp
    include auvsi_suas::jpeg-turbo.pp
    include auvsi_suas::matplotlib.pp
    include auvsi_suas::mysql.pp
    include auvsi_suas::ntp.pp
    include auvsi_suas::numpy.py
    include auvsi_suas::opencv.pp
    include auvsi_suas::openssh.pp 
    include auvsi_suas::php.pp
    include auvsi_suas::pprof.pp
    include auvsi_suas::protobuf.pp
    include auvsi_suas::pydev.pp
    include auvsi_suas::python.pp
    include auvsi_suas::qt.pp
    include auvsi_suas::rsync.pp
    include auvsi_suas::subversion.pp 
    include auvsi_suas::sqlite.pp
    include auvsi_suas::stdlib.pp
    include auvsi_suas::texlive.pp 
    include auvsi_suas::tftp.pp
    include auvsi_suas::vim.pp
}

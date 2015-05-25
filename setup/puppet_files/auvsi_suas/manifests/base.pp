# AUVSI SUAS Puppet Module: base
# Base, core system setup
# ==============================================================================

# Should be required by anything that needs to install or use packages
class auvsi_suas::base {
    require auvsi_suas::apt_sources

    # Install python and pip
    class { 'python' :
        version => 'system',
        pip     => true,
    }

    # Some core programs
    $package_deps = [
        "ntp",
        "openssh-client",
        "openssh-server",
        "rsync",
        "vim",
        "git",
    ]
    package { $package_deps:
        ensure => "latest",
    }
}

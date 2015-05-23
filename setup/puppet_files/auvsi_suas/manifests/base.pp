# AUVSI SUAS Puppet Module: base
# Base, core system setup
# ==============================================================================

class auvsi_suas::base {
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

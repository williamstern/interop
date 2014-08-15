# AUVSI SUAS Puppet Module: git
# ==============================================================================

# git module definition
class auvsi_suas::git {

    # Package list
    $package_deps = ["git"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


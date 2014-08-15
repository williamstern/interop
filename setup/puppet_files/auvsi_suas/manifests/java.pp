# AUVSI SUAS Puppet Module: java
# ==============================================================================

# java module definition
class auvsi_suas::java {

    # Package list
    $package_deps = ["openjdk-6-jdk",
                     "openjdk-6-jre",
                     "openjdk-7-jdk",
                     "openjdk-7-jre"]

    # Install packages
    package { $package_deps:
        ensure => "latest"
    }
}


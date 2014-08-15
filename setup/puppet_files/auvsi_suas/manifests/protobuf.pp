# AUVSI SUAS Puppet Module: protobuf
# ==============================================================================

# protobuf module definition
class auvsi_suas::protobuf {

    # Package list
    $package_deps = ["libprotobuf-dev",
                     "protobuf-compiler",
                     "libprotobuf-java",
                     "python-protobuf"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}


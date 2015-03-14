# AUVSI SUAS Puppet Module: chrome
# Installs the latest Chrome web browser.
# ==============================================================================

include apt

# chrome module definition
class auvsi_suas::chrome {

    # Google Chrome repo
    apt::source { "google-chrome":
        location        => "http://dl.google.com/linux/chrome/deb/",
        release         => "stable",
        repos           => "main",
        key             => "7FAC5991",
        key_source      => "https://dl-ssl.google.com/linux/linux_signing_key.pub",
        include_src     => false,
    }

    # Package list
    $package_deps = ["google-chrome-stable"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
        require => Apt::Source["google-chrome"],
    }
}

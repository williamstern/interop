# AUVSI SUAS Puppet Module: chrome
# ==============================================================================

# chrome module definition
class auvsi_suas::chrome {

    # Place the Google Chrome deb file
    file { "/tmp/google-chrome.deb":
        ensure => present,
        source => "puppet:///modules/auvsi_suas/google-chrome-stable_current_amd64.deb"
    }

    # Run the deb installer
    exec { "google-chrome-install":
        require => File["/tmp/google-chrome.deb"],
        command => "sudo dpkg -i /tmp/google-chrome.deb"
    }
}

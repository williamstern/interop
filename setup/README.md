AUVSI SUAS Setup Scripts
================================================================================

This folder contains setup scripts to automatically install dependencies for
development and deployment of the AUVSI SUAS software systems.

To automatically build and setup a virtual machine, install
[Vagrant](https://www.vagrantup.com/), change into this directory, and run:

``` sh
vagrant up
```

This will download an Ubuntu base image, boot it and execute the Puppet
manifest. Port 80 and 8080 will be forwarded from the guest to the host to
allow access to the SUAS server.

To setup a physical or prebuilt virtual machine, change the working directory
to this directory, and execute script:

``` sh
./setup.sh
```

The automated setup script performs the following actions:
  1. Updates the package list
  2. Ugrades old packages to latest
  3. Installs the puppet package
  4. Downloads puppet modules (e.g. aptitude module)
  5. Launches automated dependency setup via puppet scripts
  6. Backups any existing database
  7. Creates new database with initial test admin
     (username: testadmin, password: testpass)

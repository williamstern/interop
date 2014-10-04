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
manifest.  Port 8080 will be forwarded from the guest to the host to allow
access to the SUAS server.

To setup a physical or prebuilt virtual machine, change the working directory
to this directory, and execute scripts:

``` sh
./init.sh
./setup.sh
```

The init.sh script prepares the machine for automated setup. This includes
updating the system and installing Puppet. The setup.sh script executes the
Puppet automated setup scripts.

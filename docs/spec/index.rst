Interoperability Specification
==============================

This section describes the interoperability interface that is
implemented by the AUVSI SUAS competition server. Teams should use this
documentation to integrate with the competition server.

Hostname & Port
---------------

The competition will specify the hostname and port during the competition.
Teams will not have this during the development and testing period. For testing
purposes, teams can use the provided competition server to evaluate their
system. The hostname will be the IP address of the computer on which the server
is running, and the port will be the port selected when starting the server.
Teams must be able to specify this to their system during the mission. The
hostname can also be the hostname given to the computer. The hostname
"localhost" is a reserved name for the local host, and it resolves to the
loopback IP address 127.0.0.1. An example hostname and port combination is
"192.168.1.2:8080".

Relative URLs
-------------

The relative URLs are described further in the following sections. These will
not change during the competition, but rather be the same implementation that
is defined on this website. Note that the implementation may change during the
development and testing cycle to fix bugs or add features. Teams should
synchronize their code and check this documentation for updates. An example
relative URL is "/api/interop/server\_info".

Full Resource URL
-----------------

The full resource URL is the combination of the hostname, port, and relative
URL. This is the URL that must be used to make requests. An example full
resource URL is "http://192.168.1.2:8080/api/interop/server_info".

Further documentation about relative URLs, HTTP request types and
parameters, and returned information can be found here:

#. :doc:`login`.
   This describes how to authenticate with the competition server so
   that future requests will be authenticated. Teams cannot make other
   requests without logging in successfully.
#. :doc:`server_info`.
   This describes the interoperability interface for downloading server
   information from the competition server for purpose of displaying it.
#. :doc:`obstacles`.
   This describes the interoperability interface for downloading
   obstacle information from the competition server for purpose of
   displaying it and avoiding the obstacles.
#. :doc:`telemetry`.
   This describes the interoperability interface for uploading UAS
   telemetry information to the competition server.

--------------

Next: :doc:`login`

.. toctree::
   :hidden:

   login
   server_info
   obstacles
   telemetry

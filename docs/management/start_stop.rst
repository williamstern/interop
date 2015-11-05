Start & Stop the Server
=======================

Primary Apache Server
---------------------

The automated system setup will setup Apache to start on boot running the
interoperability server. It can be reached on the machine at http://localhost,
or on the Vagrant host at http://localhost:8000.

If necessary, the server can be manually restarted:

.. code-block:: bash

    $ sudo service apache2 restart

Development Server
------------------

The Django Web Framework also contains a developmental server that can be used
to service requests. Launching this web server for testing is described in this
section. This should generally not be necessary for teams. Teams should use
Apache, described above.

Start the Server
^^^^^^^^^^^^^^^^

The server needs an address:port for which to host the web server. The address
0.0.0.0 indicates that the server should listen on all interfaces, which allows
outside connections from other machines. Ports 80 and 8080 are standard ports
for the web. To launch the web server teams should execute the following
commands:

.. code-block:: bash

    $ cd ~/interop/server
    $ source venv/bin/activate
    $ python manage.py runserver 0.0.0.0:8080

View the Server
^^^^^^^^^^^^^^^

On the computer running the competition server, open a Chrome browser window
and navigate to `http://localhost:8080 <http://localhost:8080>`__ to view the
homepage for the web server.

Stop the Server
^^^^^^^^^^^^^^^

To stop the server, use the keyboard combination Control-C while the terminal
is in focus. This will signal the web server to shutdown.

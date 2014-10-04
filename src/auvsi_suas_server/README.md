AUVSI SUAS Source Files
================================================================================

This folder contains the AUVSI SUAS Django web server used at competition. The
directory contains the following files:

  1. auvsi_suas: The Django application that contains the main code and logic
        for the AUVSI SUAS competition. This includes various models, views, and
        control logic.
  2. auvsi_suas_server: The Django website that uses the auvsi_suas application
        to service user requests.
  3. manage.py: A utility program provided by Django which can be used to manage
        the application. This includes creating databases, running the
        development server, etc.

To start the development web server, execute:

``` sh
python manage.py runserver 8080
```

To access the web server from external machines, execute:

``` sh
python manage.py runserver 0.0.0.0:8080
```

The server will start on the local address (localhost, 127.0.0.1) with port
8080. This means the web server is providing a web page at:
http://localhost:8080/

To stop the web server, use Control-C.

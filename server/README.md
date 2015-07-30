AUVSI SUAS Source Files
================================================================================

This folder contains the AUVSI SUAS Interoperability Django web server. This
server is used at competition to run the interoperability and sense, detect,
and avoid tasks.  This directory is a Django project, with the following
components:

  1. `auvsi_suas`: The Django application that contains the main code and logic
        for the server. This includes various models, views, and control logic.
  2. `server`: The Django website that uses the `auvsi_suas` application
        to service user requests.
  3. manage.py: A utility program provided by Django which can be used to manage
        the application. This includes creating databases, running the
        development server, etc.

If the automated setup is utilized, this server is installed in a
[virtualenv](https://virtualenv.pypa.io/en/latest/). Before running the
commands below, you must activate the virtualenv with:

```sh
source venv/bin/activate
```

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

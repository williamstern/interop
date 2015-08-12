User Login
==========

Teams login to the competition server by making an HTTP POST request
with two parameters: "username" and "password". Teams only need to make
a login once before any other requests. The login request, if
successful, will return cookies that uniquely identify the user and the
current session. Teams must send these cookies to the competition server
in all future requests.

Relative URL
------------

::

    /api/login

HTTP Request Type
-----------------

::

    POST

POST Parameters
---------------

**username**. This parameter is the username that the judges give teams
during the competition. This is a unique identifier that will be used to
associate the requests as your team's.

**password**. This parameter is the password that the judges give teams
during the competition. This is used to ensure that teams do not try to
spoof other team's usernames, and that requests are authenticated with
security.

Server Response
---------------

**Code 200**. Successful logins will have a response status code of 200.
The content of the response will be a success message. The response will
also include cookies which must be sent with future requests.

**Code 400**. Unsuccessful logins will have a resposne status code of
400. The content of the response will be an error message indicating why
the request failed. Requests can fail because the request was not a POST
request, was missing one of the required parameters, or had invalid
login information.

**Code 404**. The request was made to an invalid URL, the server does
not know how to respond to such a request.

**Code 500**. The server encountered an internal error and was unable to
process the request.

--------------

Next: :doc:`server_info`

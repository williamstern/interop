Server Information
==================

Teams make requests to obtain server information for purpose of
displaying the information. This request is a GET request with no
parameters. The data returned will be in JSON format.

Relative URL
------------

::

    /api/interop/server_info

HTTP Request Type
-----------------

::

    GET

GET Parameters
--------------

**None**.

Server Response
---------------

**Code 200**. The team made a valid request. The request will be logged
to later evaluate request rates. The response will have status code 200
to indicate success, and it will have content in JSON format. This JSON
data is the server information that teams must display. The format for
the JSON data is given below.

**Code 400**. Invalid requests will return a response code of 400. A
request will be invalid if the user is not authenticated (did not made
previous login request or did not forwarded cookies), or if the user did
not make a GET request.

**Code 404**. The request was made to an invalid URL, the server does
not know how to respond to such a request.

**Code 500**. The server encountered an internal error and was unable to
process the request.

JSON Data Format
----------------

::

    {
      "server_info": {
        "message": SERVER_MESSAGE,
        "message_timestamp": SERVER_MESSAGE_TIMESTAMP
      },
      "server_time": SERVER_TIME
    }

**SERVER\_MESSAGE**: A unique message stored on the server that proves
the team has correctly downloaded the server information. This
information must be displayed as part of interoperability.

**SERVER\_MESSAGE\_TIMESTAMP**: The time the unique message was created.
This information must be displayed as part of interoperability.

**SERVER\_TIME**: The current time on the server. This information must
be displayed as part of interoperability.

--------------

Next: :doc:`obstacles`

Obstacle Information
====================

Teams make requests to obtain obstacle information for purpose of
displaying the information and for avoiding the obstacles. This request
is a GET request with no parameters. The data returned will be in JSON
format.

Relative URL
------------

::

    /api/interop/obstacles

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
data is the server information that teams must display, and it contains
data which can be used to avoid the obstacles. The format for the JSON
data is given below.

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
      "stationary_obstacles": [
        {
          "latitude": OBJECT_LATITUDE,
          "longitude": OBJECT_LONGITUDE,
          "cylinder_radius": OBJECT_CYLINDER_RADIUS,
          "cylinder_height": OBJECT_CYLINDER_HEIGHT
        }
      ],
      "moving_obstacles": [
        {
          "latitude": OBJECT_LATITUDE,
          "longitude": OBJECT_LONGITUDE,
          "altitude_msl": OBJECT_ALTITUDE,
          "sphere_radius": OBJECT_SPHERE_RADIUS
        }
      ]
    }

**Note**. The stationary\_obstacles and moving\_obstacles fields are
lists. This means that there can be 0, 1, or many objects contained
within the list. Above shows an example with 1 obstacle in each list.

**OBJECT\_LATITUDE**: The object latitude in floating point degrees.

**OBJECT\_LONGITUDE**: The object longitude in floating point degrees.

**OBJECT\_ALTITUDE**: The object's height above mean sea level (MSL) in
floating point feet.

**OBJECT\_CYLINDER\_RADIUS**: The obstacle's cylinder radius in floating
point feet.

**OBJECT\_CYLINDER\_HEIGHT**: The obstacle's cylinder height in floating
point feet.

**OBJECT\_SPHERE\_RADIUS**: The object's sphere radius in floating point
feet.

--------------

Next: :doc:`telemetry`

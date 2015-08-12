UAS Telemetry
=============

Teams make requests to upload the UAS telemetry to the competition
server. The request is a POST request with parameters "latitude",
"longitude", "altitude\_msl", and "uas\_heading".

Relative URL
------------

::

    /api/interop/uas_telemetry

HTTP Request Type
-----------------

::

    POST

POST Parameters
---------------

**latitude**. The latitude of the aircraft as a floating point degree
value. Valid values are: -90 <= latitude <= 90.

**longitude**. The longitude of the aircraft as a floating point degree
value. Valid values are: -180 <= longitude <= 180.

**altitude\_msl**. The height above mean sea level (MSL) of the aircraft
in feet as a floating point value.

**uas\_heading**. The heading of the aircraft as a floating point degree
value. Valid values are: 0 <= uas\_heading <= 360.

Server Response
---------------

**Code 200**. The team made a valid request. The information will be
stored on the competition server to evaluate various competition rules.
The content of the response will have a success message.

**Code 400**. Invalid requests will return a response code of 400. A
request will be invalid if the user is not authenticated (did not made
previous login request or did not forwarded cookies), if the user did
not make a POST request, if the user did not specify a parameter, or if
the user specified an invalid value for a parameter. The content of the
response will have an error message indicating what went wrong.

**Code 404**. The request was made to an invalid URL, the server does
not know how to respond to such a request.

**Code 500**. The server encountered an internal error and was unable to
process the request.

--------------

Next: :doc:`/hints`

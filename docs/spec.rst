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

The relative URLs (endpoints) are described further in the following sections.
The interface defined in this document is what will be used at the competition.
Only slight changes may be made leading up to the competition to fix bugs or
add features. Teams should synchronize their code and check this documentation
for updates. An example relative URL is ``/api/interop/server_info``.

Full Resource URL
-----------------

The full resource URL is the combination of the hostname, port, and relative
URL. This is the URL that must be used to make requests. An example full
resource URL is "http://192.168.1.2:8080/api/interop/server_info".

Endpoints
---------

Below are all of the endpoints provided by the server, displayed by their
relative URL, and the HTTP method with which you access them.

A quick summary of the endpoints:

* :http:post:`/api/login`: Used to authenticate with the competition server so
  that future requests will be authenticated. Teams cannot make other requests
  without logging in successfully.
* :http:get:`/api/interop/server_info`: Used to download server
  information from the competition server for purpose of displaying it.
* :http:get:`/api/interop/obstacles`: Used to download
  obstacle information from the competition server for purpose of
  displaying it and avoiding the obstacles.
* :http:post:`/api/interop/uas_telemetry`: Used to upload UAS
  telemetry information to the competition server. Uploading telemetry to this
  endpoint is required by the competition rules.


User Login
^^^^^^^^^^

.. http:post:: /api/login

   Teams login to the competition server by making an HTTP POST request with
   two parameters: "username" and "password". Teams only need to make a login
   once before any other requests. The login request, if successful, will
   return cookies that uniquely identify the user and the current session.
   Teams must send these cookies to the competition server in all future
   requests.

   **Example Request**:

   .. sourcecode:: http

      POST /api/login HTTP/1.1
      Host: 192.168.1.2:8000
      Content-Type: application/x-www-form-urlencoded

      username=testadmin&password=testpass

   **Example Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Set-Cookie: sessionid=9vepda5aorfdilwhox56zhwp8aodkxwi; expires=Mon, 17-Aug-2015 02:41:09 GMT; httponly; Max-Age=1209600; Path=/

      Login Successful.

   :form username: This parameter is the username that the judges give teams
                   during the competition. This is a unique identifier that
                   will be used to associate the requests as your team's.

   :form password: This parameter is the password that the judges give teams
                   during the competition. This is used to ensure that teams
                   do not try to spoof other team's usernames, and that
                   requests are authenticated with security.

   :resheader Set-Cookie: Upon successful login, a session cookie will be sent
                          back to the client. This cookie must be sent with
                          each subsequent request, authenticating the request.

   :status 200: Successful logins will have a response status code of 200.
                The content of the response will be a success message. The
                response will also include cookies which must be sent with
                future requests.

   :status 400: Unsuccessful logins will have a response status code of
                400. The content of the response will be an error message
                indicating why the request failed. Requests can fail because
                the request was not a POST request, was missing one of the
                required parameters, or had invalid login information.

   :status 404: The request was made to an invalid URL, the server does
                not know how to respond to such a request.

   :status 500: The server encountered an internal error and was unable to
                process the request.

Server Information
^^^^^^^^^^^^^^^^^^

.. http:get:: /api/interop/server_info

   Teams make requests to obtain server information for purpose of displaying
   the information. This request is a GET request with no parameters. The data
   returned will be in JSON format.

   **Example Request**:

   .. sourcecode:: http

      GET /api/interop/server_info HTTP/1.1
      Host: 192.168.1.2:8000
      Cookie: sessionid=9vepda5aorfdilwhox56zhwp8aodkxwi

   **Example Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "server_info": {
              "message": "Fly Safe",
              "message_timestamp": "2015-06-14 18:18:55.642000+00:00"
          },
          "server_time": "2015-08-14 03:37:13.331402"
      }


   :reqheader Cookie: The session cookie obtained from :http:post:`/api/login`
                      must be sent to authenticate the request.

   :resheader Content-Type: The response ``application/json`` on success.

   :>json object server_info: Object containing server info details.

   :>json string message: (member of ``server_info``) A unique message stored
                          on the server that proves the team has correctly
                          downloaded the server information.  This information
                          must be displayed as part of interoperability.

   :>json string message_timestamp: (member of ``server_info``) The time the
                                    unique message was created.  This
                                    information must be displayed as part of
                                    interoperability.

   :>json string server_time: The current time on the server. This information
                              must be displayed as part of interoperability.

   :status 200: The team made a valid request. The request will be logged to
                later evaluate request rates. The response will have status code
                200 to indicate success, and it will have content in JSON
                format. This JSON data is the server information that teams must
                display. The format for the JSON data is given below.

   :status 400: Invalid requests will return a response code of 400. A request
                will be invalid if the user is not authenticated (did not made
                previous login request or did not forwarded cookies), or if the
                user did not make a GET request.

   :status 404: The request was made to an invalid URL, the server does
                not know how to respond to such a request.

   :status 500: The server encountered an internal error and was unable to
                process the request.

Obstacle Information
^^^^^^^^^^^^^^^^^^^^

.. http:get:: /api/interop/obstacles

   Teams make requests to obtain obstacle information for purpose of displaying
   the information and for avoiding the obstacles. This request is a GET
   request with no parameters. The data returned will be in JSON format.

   **Example Request**:

   .. sourcecode:: http

      GET /api/interop/obstacles HTTP/1.1
      Host: 192.168.1.2:8000
      Cookie: sessionid=9vepda5aorfdilwhox56zhwp8aodkxwi

   **Example Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "moving_obstacles": [
              {
                  "altitude_msl": 189.56748784643966,
                  "latitude": 38.141826869853645,
                  "longitude": -76.43199876559223,
                  "sphere_radius": 150.0
              },
              {
                  "altitude_msl": 250.0,
                  "latitude": 38.14923628783763,
                  "longitude": -76.43238529543882,
                  "sphere_radius": 150.0
              }
          ],
          "stationary_obstacles": [
              {
                  "cylinder_height": 750.0,
                  "cylinder_radius": 300.0,
                  "latitude": 38.140578,
                  "longitude": -76.428997
              },
              {
                  "cylinder_height": 400.0,
                  "cylinder_radius": 100.0,
                  "latitude": 38.149156,
                  "longitude": -76.430622
              }
          ]
      }

   **Note**: The ``stationary_obstacles`` and ``moving_obstacles`` fields are
   lists. This means that there can be 0, 1, or many objects contained
   within each list. Above shows an example with 2 moving obstacles and 2
   stationary obstacles.

   :reqheader Cookie: The session cookie obtained from :http:post:`/api/login`
                      must be sent to authenticate the request.

   :resheader Content-Type: The response is ``application/json`` on success.

   :>json array moving_obstacles: List of zero or more moving obstacles.

   :>json array stationary_obstacles: List of zero or more stationary obstacles.

   :>json float latitude: (member of object in ``moving_obstacles`` or
                          ``stationary_obstacles``) The obstacle's current
                          altitude in degrees.

   :>json float longitude: (member of object in ``moving_obstacles`` or
                           ``stationary_obstacles``) The obstacle's current
                           longitude in degrees.

   :>json float altitude_msl: (member of object in ``moving_obstacles``) The
                              moving obstacle's current centroid altitude in
                              feet MSL.

   :>json float sphere_radius: (member of object in ``moving_obstacles``) The
                               moving obstacle's radius in feet.

   :>json float cylinder_radius: (member of object in ``stationary_obstacles``)
                                 The stationary obstacle's radius in feet.

   :>json float cylinder_height: (member of object in ``stationary_obstacles``)
                                 The stationary obstacle's height in feet.

   :status 200: The team made a valid request. The request will be logged to
                later evaluate request rates. The response will have status
                code 200 to indicate success, and it will have content in JSON
                format. This JSON data is the server information that teams
                must display, and it contains data which can be used to avoid
                the obstacles. The format for the JSON data is given below.

   :status 400: Invalid requests will return a response code of 400. A request
                will be invalid if the user is not authenticated (did not made
                previous login request or did not forwarded cookies), or if the
                user did not make a GET request.

   :status 404: The request was made to an invalid URL, the server does
                not know how to respond to such a request.

   :status 500: The server encountered an internal error and was unable to
                process the request.

UAS Telemetry
^^^^^^^^^^^^^

.. http:post:: /api/interop/uas_telemetry

   Teams make requests to upload the UAS telemetry to the competition server.
   The request is a POST request with parameters ``latitude``, ``longitude``,
   ``altitude_msl``, and ``uas_heading``.

   Each telemetry request should contain unique telemetry data. Duplicated
   data will be accepted but not evaluated.

   **Example Request**:

   .. sourcecode:: http

      POST /api/interop/uas_telemetry HTTP/1.1
      Host: 192.168.1.2:8000
      Cookie: sessionid=9vepda5aorfdilwhox56zhwp8aodkxwi
      Content-Type: application/x-www-form-urlencoded

      latitude=38.149&longitude=-76.432&altitude_msl=100&uas_heading=90

   **Example Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK

      UAS Telemetry Successfully Posted.

   :reqheader Cookie: The session cookie obtained from :http:post:`/api/login`
                      must be sent to authenticate the request.

   :form latitude: The latitude of the aircraft as a floating point degree
                   value. Valid values are: -90 <= latitude <= 90.

   :form longitude: The longitude of the aircraft as a floating point degree
                    value. Valid values are: -180 <= longitude <= 180.

   :form altitude\_msl: The height above mean sea level (MSL) of the aircraft
                        in feet as a floating point value.

   :form uas\_heading: The heading of the aircraft as a floating point degree
                       value. Valid values are: 0 <= uas\_heading <= 360.

   :status 200: The team made a valid request. The information will be stored
                on the competition server to evaluate various competition
                rules. The content of the response will have a success
                message.

   :status 400: Invalid requests will return a response code of 400. A request
                will be invalid if the user is not authenticated (did not made
                previous login request or did not forwarded cookies), if the
                user did not make a POST request, if the user did not specify a
                parameter, or if the user specified an invalid value for a
                parameter. The content of the response will have an error
                message indicating what went wrong.

   :status 404: The request was made to an invalid URL, the server does
                not know how to respond to such a request.

   :status 500: The server encountered an internal error and was unable to
                process the request.

--------------

Next: :doc:`/hints`

Configure the Server
====================

Navigate to the Admin Interface
-------------------------------

Users can configure the server using Django's admin interface. While the
competition server is running, teams should navigate to `http://localhost/admin
<http://localhost/admin>`__ if using default Apache deployment, or
`http://localhost:8080/admin <http://localhost:8080/admin>`__ if using the
Django development server. The username and password is the superuser
credentials which are setup by default to 'testadmin' and 'testpass', or is the
credentials provided when setting up the database.

Model Objects
^^^^^^^^^^^^^

Once logged in you will see a list of model objects
stored in the competition server's database. These objects represent all
data stored in the system. The models of interest include:

#. **GpsPosition**. Latitude and longitude.
#. **AerialPosition**. GPS position and altitude (in MSL).
#. **Waypoint**. Aerial position, and an order number that specifies the
   waypoint's position in a path.
#. **ServerInfo**. The server information returned to users as part of
   the interoperability task. Consists of a timestamp and message for
   the teams.
#. **ServerInfoAccessLog**. A log containing the timestamps and users
   which have made requests for server information.
#. **StationaryObstacle**. A GPS position for the centroid, and the
   radius/height of the cylinder defining the obstacle. This data will
   be returned as part of the interoperability task.
#. **MovingObstacle**. An obstacle speed, a radius for the obstacle's
   sphere, and a set of waypoints defining the obstacle's path.
#. **ObstacleAccessLog**. A log containing the timestamps and users
   which have made requests for obstacle information.
#. **UasTelemetry**. UAS telemetry that is uploaded to the server by
   teams as part of the interoperability task.
#. **FlyZone**. Specifies a valid region for which a UAS can fly. If a
   UAS is not contained within any FlyZone, then the UAS is out of
   bounds.
#. **MissionConfig**. The various settings which define a mission
   configuration. There should only be one defined for the competition.
#. **Users**. The users of the system. There will be one superuser which
   can login to the admin panel and change settings. At the competition
   this superuser will be the judges. There will also be one user for
   each team at the competition, each with a unique username and
   password. Users will authenticate against this information to verify
   identity.

Configure & View Objects
^^^^^^^^^^^^^^^^^^^^^^^^

The admin can click on an object to view data stored, to edit data stored, and
to add new data. Teams should review the :doc:`Django information
</prerequisites/django>` for how to use this interface.

How to Prepare the Server for Testing / Competition:

#. **Add Server Information**. Add a ServerInfo object that will contain
   the information for teams to download.
#. **Add Obstacles**. Add StationaryObstacle and MovingObstacle objects
   which will contain the obstacle information for teams to download.
   This will also involve creating objects like Waypoints, GpsPositions,
   etc.
#. **Add Users**. Add a user for each team with a unique username and
   password.
#. **Add Mission Configuration.** Users can specify the other mission
   parameters like no-fly zones, GPS positions of competition elements,
   the waypoint path for the competition, etc. This will be used to
   evaluate teams and view data live.
#. **Teams Compete / Judges View Live Admin Interface**. Teams will
   compete in the competition and use the interoperability interface.
   Data will be populated on the web server. Judges will use both the
   Django interface and a live-data interface to mark when teams are
   flying and to evaluate the data as it is communicated.
#. **Evaluate Data**. The ServerInfoAccessLog, ObjectAccessLog, and
   UasTelemetry objects capture the user's interaction with the system.
   Judges will use the automated scripts to evaluate users based on this
   data. This will include evaluation of communication rates, ability to
   stay in-bounds, and ability to follow waypoints.

--------------

Next: :doc:`interop_example`

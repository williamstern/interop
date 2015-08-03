Change List
===========

-  **03/26/15**: Changed from Sqlite to Postgresql databases so that the
   server can access data concurrently. Updated setup scripts to use
   postgresql and the server configuration. Updated Apache configuration
   to use parallel operations again.
-  **03/14/15**: Refactored setup files for aptitude packages to be
   simpler and easier to use. Added various setting components to enable
   deployable system. Added automatic database backup and creation.
   Added automatic Apache deployment. Updated Wiki to reflect this. Note
   this means you no longer need to execute
   ``python manage.py runserver`` as it is always deployed with Apache,
   and you should now navigate to ``localhost:80`` instead of
   ``localhost:8080``.
-  **03/13/15**: Updated setup scripts to fix a few bugs. Refactored
   Vagrantfile so that it executes the same setup script as a non-VM or
   VirtualBox setup.
-  **02/08/15**: Completed various refactors for clarity. Added stdlib
   for Puppet needed in setup scripts. Added more unicode methods to
   make setup / debugging easier. Added logging for views and debug
   output of requests on invalid request. While running server check
   ``/tmp/auvsi_suas_server.debug.log`` for useful debugging
   information. Moved caching out of model layer for less complexity.
   Increased caching amount to take more memory. Added team evaluation
   functions (interoperability rates, time spent out of boundaries,
   collisions with obstacles, satisfied waypoints, etc.) and associated
   testing routines. Added admin view to download evaluation CSV, which
   teams can use while testing to evaluate themselves. While logged in
   as admin, you can now go to ``/auvsi_admin/evaluate_teams.csv`` to
   get a CSV file that contains judging evaluation stats. Updated many
   parts of the Wiki. Added Implementation Hints to the Wiki.
-  **12/16/14**: Refactored altitudes back to MSL from AGL. This was
   done to be more consistent with the rest of the rules. Sorry for the
   back-and-forth. Added unicode string messages so the Django admin
   interface so it is easier to use when defining a mission. Added new
   models to define the rest of the mission (no-fly zones, mission
   configs, etc.)
-  **12/13/14**: Changed altitude values from mean sea level (MSL) to
   above ground level (AGL). This is both a change in representation and
   interface, done to make it easier for teams and judges. Added
   additional caching for obstacle calculations to improve max load from
   40Hz to 140Hz on test hardware. Added calculation to determine
   whether a position is inside an obstacle.
-  **11/20/14**: Added caching to increase performance. Added non-cubic
   spline interpolation for moving obstacles with 2 waypoints. Added
   better mis-configuration error handling (consecutive duplicate
   positions, unspecified positions, etc.). Removed unnecessary
   components in automated setup script. Updated auto-setup to be able
   to execute multiple times.
-  **10/04/14**: Updated the interoperability interface to be more
   consistent. The obstacle URL is updated. The JSON data format for the
   obstacle information is updated.
-  **10/04/14**: Merged patch from Michael Pratt. This patch adds
   Vagrant support for automated setup. Then added updated information
   to Wiki for using Vagrant. Thank you Michael for the help!
-  **09/23/14**: Initial source and Wiki uploaded to Github as part of
   DRAFT rules release.

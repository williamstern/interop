Mission Planner Integration
===========================

The interoperability client library comes with a sample `Mission Planner
<http://ardupilot.org/planner/docs/mission-planner-overview.html>`__
integration example. This sample lives in `client/missionplanner
<https://github.com/auvsi-suas/interop/tree/master/client/missionplanner>`__
folder in the interoperability repository. This sample may serve as a core part
of a team's interoperability system or serve as an example use of the
interoperability client library.

This sample requires that the interoperability client ``interop`` module and
its dependencies are installed on the system and available in ``PYTHONPATH``.

`auvsi_mp.py
<https://github.com/auvsi-suas/interop/blob/master/client/missionplanner/auvsi_mp.py>`__
is run as a script inside of Mission Planner. It polls for a change in aircraft
telemetry, and on change sends the telemetry to the interoperability server. It
also prints out errors detected and the average upload rate over the last 10
seconds.

Inside Mission Planner, open the script console (under Actions in the Flight
Data panel) and paste the contents of ``auvsi_mp.py`` into the window. Add a
line to add the interoperability client libraries to the system path. Modify
the script constants to provide settings like the interop server URL. When you
close the window, the script will immediately start executing.

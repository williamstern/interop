AUVSI SUAS: Interoperability Client Tools
================================================================================

## Prober

The prober is a simple use of the interoperability client which validates the
system is working and recieving data. Assuming tests passed before deployment,
this can be used to validate the system is accessible by teams.

```
python prober.py [interop_server_host] [interop_time] [username] [password] [generator] [flightsim_kml_path]
python prober.py http://localhost:80 0.1 testuser testpass zeros
```

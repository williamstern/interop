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

## Upload Targets

This script can upload targets defined in the old text file "Electronic Target
Data Format" as defined by the competition rules.

Limitations:
* Only non-ADLC targets.
* Only upload (POST), no retrieval (GET) or removal (DELETE).
* Only performs format conversion, not client-side data validation. Invalid
  data (e.g. invalid shape) will attempt to be uploaded, and the server will
  reject it.
* Does not detect duplicates- executing the script twice will upload two sets
  of targets.

```
./upload_targets.py --url http://localhost --username testuser --target_filepath ../testdata/targets.txt --imagery_dir ../testdata/
```

AUVSI SUAS: Interoperability Client Tools
=========================================

get_missions.py
---------------

This script can get the mission details from the interoperability server.

```
./get_missions.py --url http://localhost --username testuser
```

upload_targets.py
-----------------

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
./upload_targets.py --url http://localhost --username testuser --target_filepath testdata/targets.txt --imagery_dir testdata/
```

prober.py
---------

The prober is a simple use of the interoperability client which validates the
system is working and recieving data. Assuming tests passed before deployment,
this can be used to continuously validate the system is accessible by teams.

```
./prober.py http://localhost:80 0.1 testuser testpass zeros
```

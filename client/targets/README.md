# Upload Targets

This directory contains a script to upload targets defined in the text file
"Electronic Target Data Format" as defined by the competition rules.

Limitations:
* Only non-ADLC targets.
* Only upload (POST), no retrieval (GET) or removal (DELETE).
* Only performs format conversion, not client-side data validation. Invalid
  data (e.g. invalid shape) will attempt to be uploaded, and the server will
  reject it.
* Does not detect duplicates- executing the script twice will upload two sets
  of targets.

Executing the script:
```
./upload_targets.py --url http://localhost --username testuser --target_filepath ../testdata/targets.txt --imagery_base_filepath ../testdata/
```

# Prepare SanntiS GFF files for webuploader

This script prepares [SanntiS](https://github.com/Finn-Lab/SanntiS) GFF files for uploading into the EMG API.

It does a few things:
- filters away any BGCs in the GFFs that are shorted than 3000bp
- renames contigs to include the ERZ accession and use `-` in place of `_`
- puts th GFFs into an `out_dir`

Run it with something like: 
```bash
mkdir out
python3 prepare_sanntis_gffs.py test_data/gff_paths.txt out
```
There are no dependencies.

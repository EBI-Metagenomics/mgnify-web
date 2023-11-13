# Prepare EEZ JSON data from a shapefile

This script converts Exclusive Economic Zone (EEZ) data from a given shapefile into a JSON object that gets stored in the specified output path. The main reason this was created, was to provide a way for the MGnify web client to retrieve information about the Sovereigns that oversee any given EEZ, based on its MRGID. 
It is recommended that Shapefiles are sourced from [Marine Regions](https://marineregions.org/downloads.php).
This script accepts 2 arguments:
- `shapefile_path`: The path to the shapefile that contains the EEZ data
- `output_path`: The path to the output file that will contain the JSON object.
When you download a shapefile from Marine Regions, you will get a zip file containing a number of files. For this script to work properly, the shapefile must exist in a directory that contains all the other files from the original zip file. For example, if you download a shapefile from marine regions, you will get a zip file containing the following files:
- LICENSE_EEZ_v12.txt (this may have a version number emg _v12 appended)
- eez_v12.shx
- eez_v12.shp
- eez_v12.qmd
- eez_v12.prj
- eez_v12.dbf
- eez_v12.cpg
- eez_boundaries_v12.shx
- eez_boundaries_v12.shp
- eez_boundaries_v12.qmd
- eez_boundaries_v12.prj
- eez_boundaries_v12.dbf
- eez_boundaries_v12.cpg

Note that the version number i.e _v12 may vary.

To run the script, type in the command:
```python3 prepare_eez_data.py <shapefile_path> <output_path>```
The dependencies are defined in the requirements.txt file.

# Prepare EEZ JSON data from a shapefile

This scripts is used to map the sovereign states of Exclusive Economic zones gotten from a given shapefile, with their respective ABS statuses as gotten from a specified CSV file. The output is a JSON object that contains the mapping of the sovereign states to their respective ABS statuses. The JSON object is written to a file specified by the user. The output file is meant to be used by the MGnify web client to display the ABS metadata for the Samples. 
It is recommended that Shapefiles are sourced from [Marine Regions](https://marineregions.org/downloads.php).
This script accepts 3 arguments:
- `shapefile_path`: The path to the shapefile that contains the EEZ data
- `abs_csv_file`: The path to the CSV file that contains the ABS statuses of the sovereign states
- `output_json_file`: The path to the output file that will contain the JSON object.
The arguments can be passed in 2 ways:
- By specifying the arguments in the command line along with the script. For example:
```python3 prepare_eez_data.py <shapefile_path> <abs_csv_file> <output_json_file>```
- By specifying the arguments one at a time after initiating the script. For example:
```python3 prepare_eez_data.py``` 
```Enter the path to the shapefile: <shapefile_path>```
```Enter the path to the ABS CSV file: <abs_csv_file>```
```Enter the path to the output JSON file: <output_json_file>```

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

## Testing
There is a test_data folder that contains the abs_info.csv and test_output.json files for testing purposes.
The eez_v12 folder has been gitignored due to it's size. To download eez shapefile data, you can use this link: https://www.marineregions.org/downloads.php#eezshape

To run the script, type in the command:
```python3 prepare_eez_data.py <shapefile_path> <output_path>```
The dependencies are defined in the requirements.txt file.

import geopandas as gpd
import json
import argparse
import logging
import pandas as pd

# Configure logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def load_csv(csv_file):
    try:
        csv_data = pd.read_csv(csv_file)
        return csv_data
    except FileNotFoundError:
        logger.error(f"CSV file '{csv_file}' not found.")
        return None


def find_country_and_status_for_sovereign(row, csv_data):
    country_status_mapping = {}

    for i in range(1, 3):  # Assuming there are up to 5 SOVEREIGN columns (SOVEREIGN1 to SOVEREIGN5)
        sovereign_col = f'SOVEREIGN{i}'
        sovereign_value = row[sovereign_col]

        if pd.notna(sovereign_value):
            match = csv_data[csv_data['Country'] == sovereign_value]
            if not match.empty:
                status_col = f'SOVEREIGN{i}_ABS_STATUS'
                status_value = match['Status'].values[0]

                # Convert int64 to Python integer
                status_value = int(status_value)

                country_status_mapping[status_col] = status_value

    return country_status_mapping


def main():
    parser = argparse.ArgumentParser(description="Shapefile to JSON Converter")
    parser.add_argument("shapefile_path", type=str, nargs="?", help="Path to the input shapefile")
    parser.add_argument("output_json_file", type=str, nargs="?", help="Path to the output JSON file")
    parser.add_argument("csv_file", type=str, nargs="?", help="Path to the input CSV file")

    args = parser.parse_args()

    if not args.shapefile_path:
        shapefile_path = input("Enter the path to the input shapefile: ")
    else:
        shapefile_path = args.shapefile_path

    if not args.output_json_file:
        output_json_file = input("Enter the path to the output JSON file: ")
    else:
        output_json_file = args.output_json_file

    if not args.csv_file:
        csv_file = input("Enter the path to the input CSV file: ")
    else:
        csv_file = args.csv_file

    logger.info(f"Converting shapefile '{shapefile_path}' to JSON...")

    # Load the EEZ shapefile
    eez_gdf = gpd.read_file(shapefile_path)

    # Load the CSV data
    csv_data = load_csv(csv_file)
    if csv_data is None:
        return

    json_data = []  # Initialize an empty list to store JSON objects

    for _, row in eez_gdf.iterrows():
        # Remove the "geometry" key from the row
        row_data = row.drop('geometry').to_dict()

        # Find the country and status for each SOVEREIGN column
        country_status_mapping = find_country_and_status_for_sovereign(row, csv_data)

        # Replace NaN values with null in the mapping
        for key, value in country_status_mapping.items():
            if pd.isna(value):
                country_status_mapping[key] = None

        row_data.update(country_status_mapping)

        # Append the modified row data to the JSON list
        json_data.append(row_data)

    # Replace NaN values with null in the entire JSON data
    for i, entry in enumerate(json_data):
        for key, value in entry.items():
            if pd.isna(value):
                json_data[i][key] = None

    # Write the JSON list to the output JSON file
    with open(output_json_file, 'w') as json_file:
        json.dump(json_data, json_file, indent=2)

    logger.info(f"JSON data saved to {output_json_file}")


if __name__ == "__main__":
    main()

import geopandas as gpd
import json
import logging
import pandas as pd

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class EezAbsMapper:
    def __init__(self):
        self.shapefile_path = None
        self.abs_csv_file = None
        self.output_json_file = None
        self.abs_csv_data = None
        self.eez_shapefile_data = None
        self.eez_with_abs_json_data = []

    def accept_input_parameters(self, shapefile_path=None, abs_csv_file=None, output_json_file=None):
        self.shapefile_path = input(
            "Enter the path to the input shapefile: ") if shapefile_path is None else shapefile_path
        self.abs_csv_file = input("Enter the path to the ABS data CSV file: ") if abs_csv_file is None else abs_csv_file
        self.output_json_file = input(
            "Enter the path to the output JSON file: ") if output_json_file is None else output_json_file

    def load_eez_data_from_shape_file(self):
        logger.info(f"Loading shapefile '{self.shapefile_path}'...")
        self.eez_shapefile_data = gpd.read_file(self.shapefile_path)

    def load_abs_data_from_csv(self):
        logger.info(f"Loading ABS data from '{self.abs_csv_file}'...")
        try:
            self.abs_csv_data = pd.read_csv(self.abs_csv_file)
        except FileNotFoundError:
            logger.error(f"{self.abs_csv_file = } not found.")
            self.abs_csv_data = None

    def get_eez_sovereigns_abs_status(self, row):
        sovereigns_abs_status_mapping = {}

        for i in range(1, 3):
            sovereign_col = f'SOVEREIGN{i}'
            sovereign_name = row[sovereign_col]

            if pd.isna(sovereign_name):
                continue

            match = self.abs_csv_data[self.abs_csv_data['Country'] == sovereign_name]
            if match.empty:
                continue
            abs_status_col = f'SOVEREIGN{i}_ABS_STATUS'
            abs_status_value = match['Status'].values[0]

            abs_status_value = int(abs_status_value)

            sovereigns_abs_status_mapping[abs_status_col] = abs_status_value

        return sovereigns_abs_status_mapping

    def append_abs_status_to_eez_data(self):
        if self.eez_shapefile_data is None or self.abs_csv_data is None:
            logger.error("Shapefile data or ABS CSV data is not loaded. Cannot proceed.")
            return

        logger.info("Processing data to get sovereigns' ABS status...")

        for _, row in self.eez_shapefile_data.iterrows():
            row_data = row.drop('geometry').to_dict()

            sovereigns_abs_status = self.get_eez_sovereigns_abs_status(row)

            for key, value in sovereigns_abs_status.items():
                if pd.isna(value):
                    sovereigns_abs_status[key] = None

            row_data.update(sovereigns_abs_status)

            self.eez_with_abs_json_data.append(row_data)

    def output_results_to_json_file(self):
        if not self.eez_with_abs_json_data:
            logger.error("No data to save. Run 'get_sovereigns_abs_status' first.")
            return

        logger.info(f"Saving JSON data to '{self.output_json_file}'...")

        # Replace NaN values with null in the entire JSON data, as NaN is not a valid JSON value
        for i, entry in enumerate(self.eez_with_abs_json_data):
            for key, value in entry.items():
                if pd.isna(value):
                    self.eez_with_abs_json_data[i][key] = None

        with open(self.output_json_file, 'w') as json_file:
            json.dump(self.eez_with_abs_json_data, json_file, indent=2)

        logger.info(f"JSON data saved to {self.output_json_file}")


if __name__ == "__main__":
    mapper = EezAbsMapper()
    mapper.accept_input_parameters()
    mapper.load_eez_data_from_shape_file()
    mapper.load_abs_data_from_csv()
    mapper.append_abs_status_to_eez_data()
    mapper.output_results_to_json_file()

import unittest
import os
from prepare_eez_abs_data import EezAbsMapper  # Replace 'mymodule' with the actual module name


class TestEezAbsMapper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Define the paths to the existing test shapefile and ABS data
        cls.shapefile_path = 'test_data/eez_v12/eez_v12.shp'
        cls.abs_csv_path = 'test_data/abs_info.csv'
        cls.output_json_file = 'test_data/test_output.json'

    def setUp(self):
        self.mapper = EezAbsMapper()
        self.mapper.accept_input_parameters(self.shapefile_path, self.abs_csv_path, self.output_json_file)
        self.mapper.load_eez_data_from_shape_file()
        self.mapper.load_abs_data_from_csv()
        self.mapper.append_abs_status_to_eez_data()

    def test_append_abs_status_to_eez_data(self):
        self.assertTrue(len(self.mapper.eez_with_abs_json_data) > 0)

    def test_output_results_to_json_file(self):
        output_json_path = self.output_json_file
        self.assertTrue(os.path.isfile(output_json_path))


if __name__ == '__main__':
    unittest.main()

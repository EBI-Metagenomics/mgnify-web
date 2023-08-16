import unittest
import httpretty
import tempfile
import shutil
import os
from prepare_motus_crates.motus_ro_crates_preparer import MotusRoCratesPreparer


class TestMotusCratePreparer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_zip_url = "http://ftp.ebi.ac.uk/pub/databases/metagenomics/temp/motus_web/SRR5787994.tar.gz"
        self.destination_folder = self.temp_dir

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @httpretty.activate
    def test_prepare_motus_ro_crate_integration(self):
        import urllib.request
        actual_gzip_file_url = "http://ftp.ebi.ac.uk/pub/databases/metagenomics/temp/motus_web/SRR5787994.tar.gz"
        actual_gzip_file_path = os.path.join(self.temp_dir, "actual_gzip_file.tar.gz")
        urllib.request.urlretrieve(actual_gzip_file_url, actual_gzip_file_path)

        # Read the content of the gzip file
        with open(actual_gzip_file_path, 'rb') as gzip_file:
            gzip_file_content = gzip_file.read()

        # Mock HTTP response with the actual gzip file content
        httpretty.register_uri(
            httpretty.GET, self.original_zip_url,
            body=gzip_file_content, status=200
        )

        # Create the MotusCratePreparer instance
        preparer = MotusRoCratesPreparer(self.original_zip_url, self.destination_folder)

        # Call the method to be tested
        preparer.prepare_motus_ro_crate()

        print("destination_folder")
        print(self.destination_folder)
        print(os.listdir(self.destination_folder))
        print((os.path.join(self.destination_folder, "ro-crate-metadata.json")))

        # Assert that the integration worked as expected
        self.assertTrue(os.path.exists(os.path.join(self.destination_folder + '/' + "motus_SRR5787994/", "ro-crate"
                                                                                                         "-metadata"
                                                                                                         ".json")))
        # Add more assertions based on the expected outcomes of the integration


if __name__ == '__main__':
    unittest.main()

import argparse
import datetime
import glob
import json
import logging
import os
from urllib.parse import urljoin
from uuid import uuid4

import requests
import shutil
import tarfile
from ro_crate_ui_assets_provider import RoCrateUIAssetsProvider
from tqdm import tqdm
from bs4 import BeautifulSoup
from arcp import arcp_location


class MotusRoCratesPreparer:
    def __init__(self, original_ro_crate_path, destination_folder_path, extract_multiple=False):
        self.extract_multiple = extract_multiple
        self.original_ro_crate_zip_url = None if extract_multiple else original_ro_crate_path
        self.list_of_links_to_return = []
        self.original_ro_crate_path = original_ro_crate_path
        self.destination_folder_path = destination_folder_path
        self.srr_value = None
        self.downloaded_ro_crate_zip_temp_dir = None
        self.downloaded_ro_crate_zip_file_path = None
        self.multiqc_path = None
        self.krona_files = None
        self.ro_crate_output_folder_name = None
        self.raw_ro_crate_metadata = None
        self.ro_crate_metadata_html = None
        self.ro_crate_asset_provider = RoCrateUIAssetsProvider()

    def prepare_motus_ro_crate(self):
        logging.info("Starting the script.")

        try:
            self.setup_logging()
            self.extract_files_from_subdirectories(self.original_ro_crate_path)
            for source in self.list_of_links_to_return:
                self.original_ro_crate_zip_url = source
                self.create_ro_crate_temp_dir()
                self.get_srr_value()
                self.download_ro_crate_zip_file()
                self.extract_downloaded_ro_crate_zip_file()
                self.find_multiqc_report()
                self.find_krona_files()
                self.create_ro_crate_output_folder()
                self.copy_files_to_ro_crate_output_folder()
                self.add_home_button_navigation_to_multiqc_report()
                self.add_home_button_navigation_to_krona_files()
                self.create_ro_crate_metadata()
                self.create_html_from_ro_crate_metadata()
                self.create_ro_crate_preview_html()
                self.zip_ro_crate_output_folder()
                self.clean_up()
        except Exception as e:
            logging.error(str(e))
            raise

    @staticmethod
    def setup_logging():
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )

    def create_ro_crate_temp_dir(self):
        self.downloaded_ro_crate_zip_temp_dir = f"{self.destination_folder_path}_temp"
        os.makedirs(self.downloaded_ro_crate_zip_temp_dir, exist_ok=True)

    def get_srr_value(self):
        filename = os.path.basename(self.original_ro_crate_zip_url)
        self.srr_value = filename.split('.')[0]

    def get_srr_folder_path(self):
        return os.path.join(self.downloaded_ro_crate_zip_temp_dir, self.srr_value)

    def download_ro_crate_zip_file(self):
        try:
            response = requests.get(self.original_ro_crate_zip_url, stream=True)
            response.raise_for_status()  # Raises an HTTPError if the response status is not OK (200)

            zip_file_path = os.path.join(self.downloaded_ro_crate_zip_temp_dir,
                                         os.path.basename(self.original_ro_crate_zip_url))
            total_size = int(response.headers.get('content-length', 0))

            with open(zip_file_path, 'wb') as f, tqdm(total=total_size, unit='B', unit_scale=True,
                                                      desc="Downloading") as pbar:
                for data in response.iter_content(chunk_size=8192):
                    f.write(data)
                    pbar.update(len(data))

            self.downloaded_ro_crate_zip_file_path = zip_file_path
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to download the zip file from {self.original_ro_crate_zip_url}: {e}")

    def extract_downloaded_ro_crate_zip_file(self):
        with tarfile.open(self.downloaded_ro_crate_zip_file_path, 'r:gz') as tar:
            members = tar.getmembers()
            with tqdm(total=len(members), desc="Extracting files") as pbar:  # Add tqdm here
                for member in members:
                    tar.extract(member, path=self.downloaded_ro_crate_zip_temp_dir)
                    pbar.update(1)

    def find_multiqc_report(self):
        srr_folder_path = self.get_srr_folder_path()
        self.multiqc_path = glob.glob(os.path.join(srr_folder_path, 'qc', 'multiqc', 'multiqc_report.html'))

    def find_krona_files(self):
        srr_folder_path = self.get_srr_folder_path()
        self.krona_files = [file for file in glob.glob(os.path.join(srr_folder_path, 'taxonomy', '*', 'krona.html'))
                            if not file.endswith('.DS_Store')]

    def create_ro_crate_output_folder(self):
        self.ro_crate_output_folder_name = os.path.join(self.destination_folder_path, f"motus_{self.srr_value}")
        os.makedirs(self.ro_crate_output_folder_name, exist_ok=True)

    def copy_files_to_ro_crate_output_folder(self):
        with tqdm(total=len(self.krona_files) + 1, desc="Copying files") as pbar:
            if self.multiqc_path:
                shutil.copy2(self.multiqc_path[0], os.path.join(self.ro_crate_output_folder_name, 'multiqc_report.html'))
                pbar.update(1)

            if self.krona_files:
                for krona_file in self.krona_files:
                    subfolder_name = os.path.basename(os.path.dirname(krona_file))
                    krona_dest_path = os.path.join(self.ro_crate_output_folder_name, f'krona_{subfolder_name}.html')
                    shutil.copy2(krona_file, krona_dest_path)
                    pbar.update(1)

    def add_home_button_navigation_to_multiqc_report(self):
        if not self.multiqc_path:
            return
        multiqc_report_path = self.multiqc_path[0]

        with open(multiqc_report_path, 'r') as f:
            multiqc_content = f.read()

        updated_multiqc_content = f"{self.ro_crate_asset_provider.home_button_navigation_script}\n{self.ro_crate_asset_provider.home_button_styling}\n{multiqc_content}"

        new_multiqc_report_path = os.path.join(self.ro_crate_output_folder_name, 'multiqc_report.html')
        with open(new_multiqc_report_path, 'w') as f:
            f.write(updated_multiqc_content)

    def add_home_button_navigation_to_krona_files(self):
        if not self.krona_files:
            return
        for krona_file in self.krona_files:
            subfolder_name = os.path.basename(os.path.dirname(krona_file))
            krona_dest_path = os.path.join(self.ro_crate_output_folder_name, f'krona_{subfolder_name}.html')

            with open(krona_file, 'r') as f:
                krona_content = f.read()

            updated_krona_content = f"{self.ro_crate_asset_provider.home_button_navigation_script}\n{self.ro_crate_asset_provider.home_button_styling}\n{krona_content}"

            with open(krona_dest_path, 'w') as f:
                f.write(updated_krona_content)

    def create_ro_crate_preview_html(self):
        include_krona_files = bool(self.krona_files)
        include_multiqc_report = bool(self.multiqc_path)
        preview_content = self.ro_crate_asset_provider.generate_preview_html(self.srr_value,
                                                                             self.downloaded_ro_crate_zip_temp_dir,
                                                                             self.ro_crate_metadata_html,
                                                                             include_krona_files,
                                                                             include_multiqc_report)
        preview_html_path = os.path.join(self.ro_crate_output_folder_name, 'ro-crate-preview.html')
        with open(preview_html_path, 'w') as f:
            f.write(preview_content)

    def create_ro_crate_metadata(self):
        metadata = {
            "@context": "https://w3id.org/ro/crate/1.0/context",
            "conformsTo": {
                "@id": "https://w3id.org/ro/wfrun/process/0.1"
            },
            "@graph": [],
        }

        ro_crate_root_directory = {
            "@id": "./",
            "@type": "Dataset",
            "conformsTo": {
                "@id": "https://w3id.org/ro/wfrun/process/0.1"
            },
            "creator": {
                "@id": "https://ror.org/02catss52",
                "@type": "Organisation"
            },
            "datePublished": datetime.datetime.now().strftime("%Y-%m-%d"),
            "description": "mOTUs is a containarised pipeline for profiling shotgun metagenomic data.",
        }
        metadata["@graph"].append(ro_crate_root_directory)

        motus_id_prefix = f"motus_{self.srr_value}/"
        if self.krona_files:
            for krona_file in self.krona_files:
                if krona_file.endswith('LSU/krona.html'):
                    # metadata["@graph"][0]["hasPart"].append({
                    metadata["@graph"].append({
                        "@id": "krone_LSU.html",
                        "@type": "Dataset",
                        "name": "krona_LSU.html",
                        "datePublished": datetime.datetime.now().strftime("%Y-%m-%d"),
                    })
                if krona_file.endswith('SSU/krona.html'):
                    metadata["@graph"].append({
                        "@id": "krona_SSU.html",
                        "@type": "Dataset",
                        "name": "krona_SSU.html",
                        "datePublished": datetime.datetime.now().strftime("%Y-%m-%d"),
                    })

        if self.multiqc_path:
            metadata["@graph"].append({
                "@id": "multiqc_report.html",
                "@type": "Dataset",
                "name": "multiqc_report.html",
                "datePublished": datetime.datetime.now().strftime("%Y-%m-%d"),
            })

        metadata["@graph"].append({
            "@id": "ro-crate-metadata.json",
            "@type": "CreativeWork",
            "name": "ro-crate-metadata.json",
            "conformsTo": {
                "@id": "https://w3id.org/ro/crate/1.1"
            },
            "about": {
                "@id": "./"
            },
            "datePublished": datetime.datetime.now().strftime("%Y-%m-%d"),
        })
        metadata["@graph"].append({
            "@id": "ro-crate-preview.html",
            "@type": "CreativeWork",
            "name": "ro-crate-preview.html",
            "datePublished": datetime.datetime.now().strftime("%Y-%m-%d"),
        })

        metadata["@graph"].append({
            "@id": '#' + uuid4().hex,
            "@type": "CrateAction",
            "agent": [
                {
                    "@id": "https://ror.org/02catss52",
                    "@type": "Organisation"
                }
            ],
            "description": "mOTUs is a containarised pipeline for profiling shotgun metagenomic data.",
            "endTime": datetime.datetime.now().strftime("%Y-%m-%d"),
            "instrument": [
                {
                    "@id": "https://github.com/EBI-Metagenomics/motus_pipeline",
                    "@type": "SoftwareApplication"
                }
            ],
            "name": "mOTUs run on " + self.srr_value,
            "result": [
                {
                    "@id": self.original_ro_crate_path,
                    "@type": "Dataset"
                }
            ],
        })

        parent_arcp = arcp_location(self.original_ro_crate_path)
        directory_metadata = {
            "@id": self.original_ro_crate_path,
            "@type": "Dataset",
            "@base": parent_arcp,
            "creator": {
                "@id": "https://ror.org/02catss52",
                "@type": "Organisation"
            },
            "hasPart": [],
        }

        with tqdm(total=len(os.listdir(self.downloaded_ro_crate_zip_temp_dir)), desc="Creating metadata") as pbar:
            for root, _, files in os.walk(self.downloaded_ro_crate_zip_temp_dir):
                files = [filename for filename in files if not filename.endswith('.DS_Store')]

                for filename in files:
                    file_metadata = {
                        "@id": parent_arcp + os.path.relpath(os.path.join(root, filename),
                                                             self.downloaded_ro_crate_zip_temp_dir),
                        "@type": "Dataset",
                        "name": filename,
                    }
                    directory_metadata["hasPart"].append(file_metadata)
                pbar.update(1)
            metadata["@graph"].append(directory_metadata)

        ro_crate_metadata_path = os.path.join(self.ro_crate_output_folder_name, 'ro-crate-metadata.json')
        self.raw_ro_crate_metadata = metadata
        with open(ro_crate_metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    def create_html_from_ro_crate_metadata(self):
        self.ro_crate_metadata_html = self.ro_crate_asset_provider.generate_metadata_html(self.raw_ro_crate_metadata)

    def zip_ro_crate_output_folder(self):
        shutil.make_archive(self.ro_crate_output_folder_name, 'zip', self.ro_crate_output_folder_name)

    def clean_up(self):
        shutil.rmtree(self.downloaded_ro_crate_zip_temp_dir)

    def extract_files_from_subdirectories(self, url):
        if not self.extract_multiple:
            self.list_of_links_to_return.append(url)
            return
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch {url}")
            return
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')

        links = links[5:]
        for link in links:
            href = link.get('href')
            if href.endswith('.md5'):
                continue
            if href == '../' or not href.endswith('/'):
                href = urljoin(url, href)
                if not href.endswith('.tar.gz'):
                    continue
                self.list_of_links_to_return.append(href)
                continue
            subdir_url = urljoin(url, href)
            self.extract_files_from_subdirectories(subdir_url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Prepare Motus crate.')
    parser.add_argument('original_crate_zip_url', type=str, help='URL to the original crate zip file.')
    parser.add_argument('destination_folder', type=str, help='Destination folder path.')
    parser.add_argument('--extract_multiple', action='store_true', help='Prepare multiple RO crates from a list of '
                                                                        'directories.')
    args = parser.parse_args()
    preparer = MotusRoCratesPreparer(args.original_crate_zip_url, args.destination_folder, args.extract_multiple)
    preparer.prepare_motus_ro_crate()

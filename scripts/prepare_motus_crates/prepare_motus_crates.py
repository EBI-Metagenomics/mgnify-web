import argparse
import glob
import json
import logging
import os
import requests
import shutil
import tarfile


class MotusCratePreparer:
    def __init__(self, original_crate_zip_url, destination_folder):
        self.original_crate_zip_url = original_crate_zip_url
        self.destination_folder = destination_folder
        self.srr_value = None
        self.temp_dir = None
        self.multiqc_path = None
        self.krona_files = None
        self.output_folder_name = None

    def prepare_motus_crate(self):
        logging.info("Starting the script.")

        try:
            self.setup_logging()
            self.create_temp_dir()
            self.get_srr_value()
            zip_file_path = self.download_zip_file()
            self.extract_zip_file(zip_file_path)
            self.find_multiqc_report()
            self.find_krona_files()
            self.create_new_folder()
            self.copy_files_to_new_folder()
            self.create_preview_html()
            self.create_ro_crate_metadata()  # Add the creation of ro-crate-metadata.json
            self.zip_new_folder()
            self.clean_up()
        except Exception as e:
            logging.error(str(e))
            raise

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )

    def create_temp_dir(self):
        self.temp_dir = f"{self.destination_folder}_temp"
        os.makedirs(self.temp_dir, exist_ok=True)

    def get_srr_value(self):
        filename = os.path.basename(self.original_crate_zip_url)
        self.srr_value = filename.split('.')[0]

    def download_zip_file(self):
        response = requests.get(self.original_crate_zip_url)
        if not response.ok:
            raise ValueError(f"Failed to download the zip file from {self.original_crate_zip_url}. "
                             f"Error code: {response.status_code}")

        zip_file_path = os.path.join(self.temp_dir, os.path.basename(self.original_crate_zip_url))
        with open(zip_file_path, 'wb') as f:
            f.write(response.content)
        return zip_file_path

    def extract_zip_file(self, zip_file_path):
        with tarfile.open(zip_file_path, 'r:gz') as tar:
            tar.extractall(self.temp_dir)

    def find_multiqc_report(self):
        srr_folder_path = os.path.join(self.temp_dir, self.srr_value)  # Use the specific SRR folder
        self.multiqc_path = glob.glob(os.path.join(srr_folder_path, 'qc', 'multiqc', 'multiqc_report.html'))
        if not self.multiqc_path:
            raise FileNotFoundError("multiqc_report.html not found in the extracted folder.")

    def find_krona_files(self):
        srr_folder_path = os.path.join(self.temp_dir, self.srr_value)  # Use the specific SRR folder
        self.krona_files = [file for file in glob.glob(os.path.join(srr_folder_path, 'taxonomy', '*', 'krona.html'))
                            if not file.endswith('.DS_Store')]
        if not self.krona_files:
            raise FileNotFoundError("No krona.html files found in the extracted folder.")

    def create_new_folder(self):
        self.output_folder_name = os.path.join(self.destination_folder, f"motus_{self.srr_value}")
        os.makedirs(self.output_folder_name, exist_ok=True)

    def copy_files_to_new_folder(self):
        shutil.copy2(self.multiqc_path[0], os.path.join(self.output_folder_name, 'multiqc_report.html'))
        for krona_file in self.krona_files:
            subfolder_name = os.path.basename(os.path.dirname(krona_file))
            krona_dest_path = os.path.join(self.output_folder_name, f'krona_{subfolder_name}.html')
            shutil.copy2(krona_file, krona_dest_path)

    def create_preview_html(self):
        srr_folder_path = os.path.join(self.temp_dir, self.srr_value)  # Use the specific SRR folder

        # Add the JavaScript script for the event listener
        js_script = """
        <script>
          function containsText(anchor, text) {
            return anchor.textContent.includes(text);
          }
        
          function handleClick(event) {
            if (window.self === window.top) {
              // We're not in an iframe, so we allow the links to work normally
              return;
            }
            event.preventDefault();
            const anchor = event.target;
            const anchorText = anchor.textContent;
            window.parent.postMessage(anchor.id, "*");
          }
        
          document.addEventListener("DOMContentLoaded", function() {
            const anchorTags = document.querySelectorAll("a");
            anchorTags.forEach(anchor => {
              const anchorText = anchor.textContent;
              if (containsText(anchor, "multiqc_report") || containsText(anchor, "krona")) {
                anchor.addEventListener("click", handleClick);
              }
            });
          });
        </script>
        """

        # Update the preview_content to include the unique IDs and the JavaScript script
        preview_content = f""" <!DOCTYPE html> <html> <head> <title>Preview</title> </head> <body> <h1>Preview of 
        Extracted HTML Files</h1> <ul> <li><a href="multiqc_report.html" 
        id="multiqc_report.html">multiqc_report.html</a></li> 
        {"".join(f'<li><a href="krona_{subfolder_name}.html" id="krona_{subfolder_name}'
                 f'.html">krona_{subfolder_name}.html</a></li>'
                 for subfolder_name in os.listdir(os.path.join(srr_folder_path, 'taxonomy'))
                 if not subfolder_name.__contains__('DS_Store') and not subfolder_name.startswith('._'))}
        </ul>
        {js_script}
        </body>
        </html>
        """

        with open(os.path.join(self.output_folder_name, 'ro-crate-preview.html'), 'w') as f:
            f.write(preview_content)

    def create_ro_crate_metadata(self):
        # Replace the placeholders below with the actual metadata content
        metadata = {
            "title": "My RO-Crate",
            "description": "This is a RO-Crate metadata file",
            # Add more metadata fields as needed
        }

        # Write the metadata to the ro-crate-metadata.json file
        ro_crate_metadata_path = os.path.join(self.output_folder_name, 'ro-crate-metadata.json')
        with open(ro_crate_metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    def zip_new_folder(self):
        shutil.make_archive(self.output_folder_name, 'zip', self.output_folder_name)
        shutil.move(f"{self.output_folder_name}.zip",
                    os.path.join(self.destination_folder, f"motus_{self.srr_value}.zip"))

    def clean_up(self):
        shutil.rmtree(self.temp_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Prepare Motus crate.')
    parser.add_argument('original_crate_zip_url', type=str, help='URL to the original crate zip file.')
    parser.add_argument('destination_folder', type=str, help='Destination folder path.')
    args = parser.parse_args()

    preparer = MotusCratePreparer(args.original_crate_zip_url, args.destination_folder)
    preparer.prepare_motus_crate()

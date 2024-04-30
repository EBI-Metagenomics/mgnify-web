import os
import datetime


class RoCrateUIAssetsProvider:
    def __init__(self):
        self.preview_html_styling = self.load_asset('assets/css/ro-crate-preview.css', 'style')
        self.ro_crate_preview_script = self.load_asset('assets/js/ro-crate-preview.js', 'script')
        self.home_button_navigation_script = self.load_asset('assets/js/home-button.js', 'script')
        self.home_button_styling = self.load_asset('assets/css/home-button.css', 'style')
        self.mgnify_logo = self.load_asset('assets/img/mgnify-logo.svg')

    @staticmethod
    def load_asset(path, asset_tag=None):
        with open(path, 'r') as f:
            content = f.read()
            return f"<{asset_tag}>{content}</{asset_tag}>" if asset_tag else content

    @staticmethod
    def generate_krona_files_list_elements(srr_folder_path):
        subfolder_links = [
            (f'<li><a href="krona_{subfolder_name}.html" id="krona_{subfolder_name}.html">'
             f'krona_{subfolder_name}.html</a></li>')
            for subfolder_name in os.listdir(os.path.join(srr_folder_path, 'taxonomy'))
            if not subfolder_name.__contains__('DS_Store') and not subfolder_name.startswith('._')
        ]
        return '\n'.join(subfolder_links)

    def generate_preview_html(self, crate_srr_value, temp_zip_dir, metadata_html, include_krona_files=False,
                              include_multiqc_report=False):
        srr_folder_path = os.path.join(temp_zip_dir, crate_srr_value)
        if include_krona_files:
            krona_files_list = self.generate_krona_files_list_elements(srr_folder_path)
        else:
            krona_files_list = ''
        published_date = datetime.datetime.now().strftime("%Y-%m-%d")

        html = (
            f"<!DOCTYPE html>\n"
            f"<html>\n"
            f"<head>\n"
            f"    <title>mOTUs details for run {crate_srr_value}</title>\n"
            f"    <meta name=\"keywords\" content=\"RO Crate\">\n"
            f"    {self.preview_html_styling}\n"
            f"</head>\n"
            f"<body>\n"
            f"<div class=\"main\">\n"
            f"    {self.mgnify_logo}\n"
            f"    <h1>mOTUs details for run {crate_srr_value}</h1>\n"
            f"    <p>Description</p>\n"
            f"    <dl>\n"
            f"        <dt>Creator</dt>\n"
            f"        <dd>EMBL-EBI</dd>\n"
            f"        <dt>Date published</dt>\n"
            f"        <dd>{published_date}</dd>\n"
            f"    </dl>\n"
            f"    <h2>Contents</h2>\n"
            f"    <div id=\"contents\">\n"
            f"        <div class=\"data-entity\">\n"
            f"            <ul>\n"
        )

        if include_multiqc_report:
            html += (
                f"                <li><a href=\"multiqc_report.html\" id=\"multiqc_report.html\">"
                f"multiqc_report.html</a></li>\n"
            )

        if include_krona_files:
            html += f"                {krona_files_list}\n"

        html += (
            f"            </ul>\n"
            f"        </div>\n"
            f"    </div>\n"
            f"    <div id=\"variables\">\n"
            f"        {metadata_html}\n"
            f"    </div>\n"
            f"</div>\n"
            f"{self.ro_crate_preview_script}\n"
            f"</body>\n"
            f"</html>"
        )
        return html

    @staticmethod
    def generate_metadata_html(raw_metadata):
        html_string = '<div id="metadata">\n'

        for entry in raw_metadata['@graph']:
            entry_id = entry['@id']
            entry_type = entry.get('@type', '')
            entry_name = entry.get('name', '')
            entry_date_published = entry.get('datePublished', '')
            entry_has_part = entry.get('hasPart', [])

            # Append the HTML for the current entry
            html_string += f'  <a id="{entry_id}" />\n'
            html_string += '  <div class="context-entity" id="">\n'
            html_string += f'    <strong>{entry_type}</strong>\n\n'
            html_string += f'    <a class="data-entity-link" href="{entry_id}">{entry_id}</a>\n\n'
            html_string += '    <p>\n'

            # Append key-value pairs for the current entry
            html_string += '      <dl>\n'
            html_string += f'        <dt>name</dt>\n        <dd>{entry_name}</dd>\n'
            html_string += f'        <dt>datePublished</dt>\n        <dd>{entry_date_published}</dd>\n'
            html_string += '      </dl>\n'

            # Append key-value pairs for the hasPart elements of the current entry
            for has_part_entry in entry_has_part:
                has_part_id = has_part_entry.get('@id', '')
                has_part_type = has_part_entry.get('@type', '')
                has_part_name = has_part_entry.get('name', '')
                has_part_date_published = has_part_entry.get('datePublished', '')

                html_string += '      <dl>\n'
                html_string += f'        <dt>@id</dt>\n        <dd>{has_part_id}</dd>\n'
                html_string += f'        <dt>@type</dt>\n        <dd>{has_part_type}</dd>\n'
                html_string += f'        <dt>name</dt>\n        <dd>{has_part_name}</dd>\n'
                html_string += f'        <dt>datePublished</dt>\n        <dd>{has_part_date_published}</dd>\n'
                html_string += '      </dl>\n'

            html_string += '    </p>\n'
            html_string += '  </div>\n'

        # Close the div tag
        html_string += '</div>\n'

        return html_string

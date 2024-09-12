import argparse
from datetime import datetime
import glob
import os
from pathlib import Path
import re
from uuid import uuid4

from jinja2 import Template
from rocrate.rocrate import ROCrate
from rocrate.model.preview import Preview
from rocrate.model.contextentity import ContextEntity


class MGnifyPreview(Preview):
    def generate_html(self):
        template = open('mgnify-rocrate-preview-template.html.j2')
        src = Template(template.read())

        def template_function(func):
            src.globals[func.__name__] = func
            return func

        @template_function
        def stringify(a):
            if type(a) is list:
                return ', '.join([stringify(aa) for aa in a])
            elif type(a) is str:
                return a
            elif hasattr(a, '_jsonld') and a._jsonld.get('name'):
                    return a._jsonld['name']
            elif type(a) is dict:
                return stringify(list(a.values()))
            else:
                return a

        @template_function
        def is_object_list(a):
            if type(a) is list:
                for obj in a:
                    if obj is not str:
                        return True
            else:
                return False

        @template_function
        def details(a):
            if type(a) is dict:
                return {k: v for k, v in a.items() if k not in ['@id', '@type']}

        template.close()
        context_entities = []
        data_entities = []
        for entity in self.crate.contextual_entities:
            context_entities.append(entity._jsonld)
        for entity in self.crate.data_entities:
            data_entities.append(entity._jsonld)
        out_html = src.render(crate=self.crate, context=context_entities, data=data_entities)
        return out_html

def create_metapuf_rocrate(gff_path: str, pride_id: str, crate_path: str):
    try:
        assembly = re.findall(r"ERZ[\d]*", gff_path)[0]
    except KeyError:
        print(f'Could not determine assembly accession from path {gff_path}')
        return

    crate = ROCrate(gen_preview=False)
    crate.add(MGnifyPreview(crate))

    # Conform to the WFRUN profile
    PC_PROFILE_ID = "https://w3id.org/ro/wfrun/process/0.3"
    pc_profile = crate.add(ContextEntity(crate, PC_PROFILE_ID, properties={
        "@type": "CreativeWork",
        "name": "Process Run Crate",
        "version": "0.3"
    }))
    crate.root_dataset["conformsTo"] = pc_profile

    crate.name = f'MetaPUF annotations for assembly {assembly}'
    crate.description = f"""MetaPUF (Metagenomic Proteins of Unknown Function) integrates meta-genomics/transcriptomics
    (using MGnify) and meta-proteomics (using PRIDE). 
    This is the MetaPUF annotations for assembly {assembly} and PRIDE dataset {pride_id}"""

    # Workflow Provenance
    sourcecode = crate.add(ContextEntity(crate, "https://github.com/PRIDE-reanalysis/MetaPUF", properties={
        "@type": "SoftwareSourceCode",
        "name": "MetaPUF",
        "url": "https://github.com/PRIDE-reanalysis/MetaPUF",
        "codeRepository": "https://github.com/PRIDE-reanalysis/MetaPUF",
        "version": "1.0.0",
    }))
    fnr = crate.add(ContextEntity(crate, "https://ror.org/039z13y21", properties={
        "@type": "Organization",
        "name": "FNR",
        "alternateName": "National Research Fund Luxembourg",
        "url": "https://www.fnr.lu"
    }))
    fnr_grant = crate.add(ContextEntity(crate, "C19/BM/13684739", properties={
        "@type": "Grant",
        "name": "C19/BM/13684739",
        "url": "https://www.fnr.lu"
    }))
    fnr_grant.append_to("funder", fnr)
    sourcecode.append_to("funding", fnr_grant)

    embl = crate.add(ContextEntity(crate, "https://ror.org/01zjc6908", properties={
        "@type": "Organization",
        "name": "EMBL",
        "alternateName": "European Molecular Biology Laboratory",
        "url": "https://www.embl.org"
    }))
    embl_grant = crate.add(ContextEntity(crate, "EMBL core funding", properties={
        "@type": "Grant",
        "name": "EMBL Core Funding",
        "url": "https://www.embl.org"
    }))
    embl_grant.append_to("funder", embl)
    sourcecode.append_to("funding", embl_grant)

    # The run
    agent = crate.add(ContextEntity(crate, "https://ror.org/02catss52", properties={
        "@type": "Organization",
        "name": "EMBL-EBI",
        "url": "https://www.ebi.ac.uk/metagenomics"
    }))
    crate.creator = agent

    fin = os.path.getctime(gff_path)

    ## Add GFF output file
    gff = crate.add_file(
        gff_path,
        properties={
            "name": "annotations gff",
            "encodingFormat": "text/x-gff3"
        }
    )

    ## Add link
    run_id = uuid4().hex
    run = crate.add(ContextEntity(crate, run_id, properties={
        "@type": "CreateAction",
        "name": f"MetaPUF annotations for {assembly}",
        "endTime": datetime.fromtimestamp(fin).isoformat(),
        "description": "",
    }))
    run.append_to("result", gff)
    run.append_to("agent", agent)
    run.append_to("instrument", sourcecode)

    ## Describe the GFF columns of interest
    gff_cols = [
            crate.add(ContextEntity(crate, 'gff_attribute_unique_peptide_to_protein_mapping', properties={
            "@type": "PropertyValue",
            "name": "Unique peptide to protein mapping (bool)",
            "description": "The boolean Unique_peptide_to_protein_mapping in the GFF column 9 distinguishes whether the mapping is ambiguous or unique.",
            "value": "Unique_peptide_to_protein_mapping",
        })),
    ]

    for col in gff_cols:
        crate.root_dataset.append_to("variableMeasured", col)

    crate.write_zip(Path(crate_path) / Path(f"metapuf_{sourcecode['version']}_{assembly}.zip"))


def main():
    parser = argparse.ArgumentParser(description="Take MetaPUF-generated GFF files and create RO-Crates for each one.")
    parser.add_argument("gff_paths", type=str, help="Glob pattern for GFF files")
    parser.add_argument("pride_id", type=str, help="PRIDE ID for all assemblies")
    parser.add_argument("--output_dir", type=str, help="Output directory for the crates", default="./crates")

    args = parser.parse_args()

    gff_files = glob.glob(args.gff_paths)

    for gff_file in gff_files:
        print(f"Processing {gff_file}")
        create_metapuf_rocrate(gff_file, args.pride_id, args.output_dir)


if __name__ == "__main__":
    main()
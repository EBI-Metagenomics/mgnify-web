from rocrate.rocrate import ROCrate
from rocrate.model.preview import Preview
from rocrate.model.contextentity import ContextEntity
from uuid import uuid4
import os
from datetime import datetime
from jinja2 import Template


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

def create_sanntis_rocrate(gff_path: str):
    try:
        assembly = 'ERZ' + gff_path.split('ERZ')[1].split('.')[0].split('_')[0]
    except:
        print(f'Could not determine assembly accession from path {gff_path}')
        return

    crate = ROCrate(gen_preview=False)
    crate.add(MGnifyPreview(crate))

    # Conform to the WFRUN profile
    PC_PROFILE_ID = "https://w3id.org/ro/wfrun/process/0.1"
    pc_profile = crate.add(ContextEntity(crate, PC_PROFILE_ID, properties={
        "@type": "CreativeWork",
        "name": "Process Run Crate",
        "version": "0.1"
    }))
    crate.root_dataset["conformsTo"] = pc_profile

    crate.name = f'SANNTIS predictions for assembly {assembly}'
    crate.description = f"""SanntiS (SMBGC Annotation using Neural Networks Trained on Interpro Signatures) predicts secondary metabolite biosynthetic gene clusters.
This is the output (a GFF feature file) of SanntiS being run on the MGnify assembly {assembly}."""

    # Workflow Provenance
    sourcecode = crate.add(ContextEntity(crate, "https://github.com/Finn-Lab/SanntiS", properties={
        "@type": "SoftwareSourceCode",
        "name": "SanntiS: SMBGC Annotation using Neural Networks Trained on Interpro Signatures",
        "alternateName": "emeraldBGC",
        "url": "https://github.com/Finn-Lab/SanntiS",
        "codeRepository": "https://github.com/Finn-Lab/SanntiS",
        "version": "0.9.3.1",
    }))
    bbsrc = crate.add(ContextEntity(crate, "https://ror.org/00cwqg982", properties={
        "@type": "Organization",
        "name": "BBSRC",
        "alternateName": "Biotechnology and Biological Sciences Research Council",
        "url": "http://www.bbsrc.ac.uk/"
    }))
    emerald_grant = crate.add(ContextEntity(crate, "BB/S009043/1", properties={
        "@type": "Grant",
        "name": "EMERALD - Enriching MEtagenomics Results using Artificial intelligence and Literature Data",
        "url": "https://gtr.ukri.org/projects?ref=BB%2FS009043%2F1"
    }))
    emerald_grant.append_to("funder", bbsrc)
    sourcecode.append_to("funding", emerald_grant)

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
        "name": f"SanntiS run on {assembly}",
        "endTime": datetime.fromtimestamp(fin).isoformat(),
        "description": "",
    }))
    run.append_to("result", gff)
    run.append_to("agent", agent)
    run.append_to("instrument", sourcecode)

    ## Describe the GFF columns of interest
    gff_cols = [
            crate.add(ContextEntity(crate, 'gff_attribute_nearest_mibig', properties={
            "@type": "PropertyValue",
            "name": "Nearest MiBIG",
            "url": "https://mibig.secondarymetabolites.org/repository",
            "description": "The nearest_MiBIG attribute in the GFF column 9 is the closest predicted BGC from the MiBIG ontology.",
            "value": "nearest_MiBIG",
            "propertyId": "https://mibig.secondarymetabolites.org/repository/@value",
        })),
        crate.add(ContextEntity(crate, 'gff_attribute_nearest_mibig_class', properties={
            "@type": "PropertyValue",
            "name": "Nearest MiBIG class",
            "url": "https://mibig.secondarymetabolites.org",
            "description": "The nearest_MiBIG_class attribute in the GFF column 9 is one of the 6 (or other) BGC types from the MiBIG ontology.",
            "value": "nearest_MiBIG_class",
            "propertyId": "https://mibig.secondarymetabolites.org/",
        }))
    ]

    for col in gff_cols:
        crate.root_dataset.append_to("variableMeasured", col)

    crate.write_zip(f"./crates/sanntis_{sourcecode['version']}_{assembly}.zip")

with open('gffPaths3.txt', 'r') as paths:
    for path in paths.readlines():
        print(path)
        create_sanntis_rocrate(path.strip())

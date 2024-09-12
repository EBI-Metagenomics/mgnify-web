# Package up a MetaPUF-created GFF file as an RO-Crate

This script is a helper that packages/publishes a GFF file, created by the [MetaPUF pipeline](https://github.com/pride-reanalysis/metapuf), as an [RO-Crate](https://www.researchobject.org/ro-crate/).

The schema of the RO-Crate is one that is supported by [MGnify](https://www.ebi.ac.uk/metagenomics): 
it contextualises the GFF file with enough metadata that it can be displayed in the MGnify Assembly Analsysis Contig Viewer (an [IGV.js](https://github.com/igvteam/igv.js/) instance) alongside other annotation tracks.

## Requirements
Python3 and pip.

## Installation
Download this `prepare_metapuf_crates` folder (e.g. as a zip from GitHub).
Or: `git clone --no-recurse-submodules https://github.com/EBI-Metagenomics/mgnify-web.git`

```bash
pip install -r requirements.txt
```

## Usage
Call the `package_metapuf_as_crates` script with the path to a GFF, and the [PRIDE](https://www.ebi.ac.uk/pride/) PXD accession of the dataset that generated the GFF.

E.g.:

```bash
python package_metapuf_as_crates.py examples/*.gff PXD005780
```

Optionally, an output directory may be specified other than the default `./crates`:

```bash
python package_metapuf_as_crates.py examples/*.gff PXD005780 --output_dir my-crates-folder
```
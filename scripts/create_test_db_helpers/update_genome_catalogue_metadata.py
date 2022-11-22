from emgapi.models import GenomeCatalogue
GenomeCatalogue.objects.filter(
    catalogue_id='human-gut-v2-0'
).update(
    unclustered_genome_count=99,
    protein_catalogue_name='UHGP',
    protein_catalogue_description='Protein coding sequences from genomes in the UHGG2.0',
    description='An update of [Almeida et al, Nature Biotechnol (2021)](https://www.nature.com/articles/s41587-020-0603-3)'
)
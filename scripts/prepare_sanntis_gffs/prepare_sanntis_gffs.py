import argparse
from pathlib import Path


def is_bgc_long_enough(annotation, min_length: int = 3000):
    fields = annotation.split('\t')
    print(fields)
    start = int(fields[3])
    end = int(fields[4])
    return (end - start) >= min_length


def rename_contig(annotation, filename):
    if annotation.startswith('ERZ'):
        return annotation
    erz = filename.split('.')[0]
    annotation = annotation.split('\t')
    annotation[0] = f"{erz}.{annotation[0].replace('_', '-')}"
    return '\t'.join(annotation)


def parse_args():
    parser = argparse.ArgumentParser(description='Prepare SanntiS GFFs for consumption by EMG webuploader')
    parser.add_argument('gffs_list_file', help='A text file with a list of GFF paths')
    parser.add_argument('out_dir', help='A directory to output the prepared GFFs into')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    print(args)

    assert Path(args.gffs_list_file).is_file()

    out_path = Path(args.out_dir)
    assert out_path.is_dir()

    with open(args.gffs_list_file, 'r') as gffs_file:
        for gff_path in gffs_file.readlines():
            gff_path = gff_path.strip(' \n\r')
            print(f'Working on {gff_path}')
            with open(gff_path, 'r') as original_gff:
                with open(out_path / Path(gff_path).name, 'w') as new_gff:
                    new_gff.write('##gff-version 3\n')
                    for annotation in original_gff.readlines():
                        if annotation.startswith('#'):
                            continue
                        if is_bgc_long_enough(annotation):
                            new_annotation = rename_contig(annotation, Path(gff_path).stem)
                            new_gff.write(new_annotation)


if __name__ == '__main__':
    main()

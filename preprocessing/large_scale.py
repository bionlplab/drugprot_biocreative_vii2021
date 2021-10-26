import collections
import os
import re
import zipfile
from pathlib import Path
from zipfile import ZipFile

import bioc
import tqdm

from drugprot_to_bioc import convert as convert_to_bioc
from postprocess import merge_sentences
from utils import chunks, FileLock


def split_files(abstract_file, entities_file, output_dir):
    cnt = collections.Counter()

    abstract_map = collections.defaultdict(list)
    with open(abstract_file, encoding='utf8') as fp:
        for line in tqdm.tqdm(fp, desc=abstract_file.stem):
            docid = line[:line.find('\t')]
            abstract_map[docid].append(line)

    # entities
    entities_map = collections.defaultdict(list)
    with open(entities_file, encoding='utf8') as fp:
        for line in tqdm.tqdm(fp, desc=entities_file.stem):
            docid = line[:line.find('\t')]
            entities_map[docid].append(line)

    print('Abstract', len(abstract_map.keys()))
    print('Entities', len(entities_map.keys()))

    docids = list(abstract_map.keys())
    for i, subdocids in tqdm.tqdm(enumerate(chunks(docids, 5000))):
        # abstract
        with open(output_dir / 'large_scale_abstracts_{}.tsv'.format(i), 'w', encoding='utf8') as fp:
            for docid in subdocids:
                for line in abstract_map[docid]:
                    fp.write(line)

        # entities
        with open(output_dir / 'large_scale_entities_{}.tsv'.format(i), 'w', encoding='utf8') as fp:
            for docid in subdocids:
                for line in entities_map[docid]:
                    fp.write(line)


def convert_to_bioc_dir(input_dir, output_dir):
    def get_index(name):
        m = re.match(r'large_scale_abstracts_(\d+)\.', name)
        if m:
            return m.group(1)
        raise ValueError('Cannot match {}'.format(name))

    with os.scandir(input_dir) as it:
        for entry in it:
            if entry.name.startswith('large_scale_abstracts'):
                i = get_index(entry.name)
                convert_to_bioc(input_dir / 'large_scale_abstracts_{}.tsv'.format(i),
                                input_dir / 'large_scale_entities_{}.tsv'.format(i),
                                None,
                                output_dir / 'large_scale_{}.xml'.format(i))


def get_zipped_file(input):
    stem = Path(input).stem
    with ZipFile(input) as myzip:
        with myzip.open(stem) as fp:
            collection = bioc.load(fp)
    return collection


def postprocess(input_dir, output_dir):
    with os.scandir(input_dir) as it:
        for entry in it:
            m = re.match(r'large_scale_(\d+)_preprocessed\.xml\.zip', entry.name)
            if m is None:
                continue

            input = Path(entry.path)
            i = m.group(1)
            output = output_dir / 'large_scale_{}_preprocessed_mergesent.xml.zip'.format(i)

            lck = FileLock(output)
            if lck.exists():
                continue

            with lck:
                print('Read {}'.format(input.name))
                stem = input.stem
                with ZipFile(input) as myzip:
                    with myzip.open(stem) as fp:
                        collection = bioc.load(fp)
                merge_sentences(collection)
                s = bioc.dumps(collection)

                print('Write {}'.format(output))
                with ZipFile(output, mode='w', compression=zipfile.ZIP_DEFLATED) as myzip:
                    myzip.writestr(stem, s)


if __name__ == '__main__':
    dir = Path.home() / 'Data/drugprot'
    data_dir = dir / 'large-scale-drugprot'

    # split_files(data_dir / 'large_scale_abstracts.tsv',
    #             data_dir / 'large_scale_entities.tsv',
    #             data_dir / 'split')

    # convert_to_bioc_dir(data_dir / 'split', data_dir / 'bioc')
    postprocess(data_dir / 'preprocessed-zip', data_dir / 'preprocessed-zip')

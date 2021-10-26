import collections
from pathlib import Path

import bioc
import tqdm


def convert(abstract_file, entities_file, relation_file, output_dir):
    docids = set()
    with open(abstract_file, encoding='utf8') as fp:
        for line in tqdm.tqdm(fp, desc=abstract_file.stem):
            toks = line.strip().split('\t')
            with open(output_dir / '{}.txt'.format(toks[0]), 'w', encoding='utf8') as fp:
                fp.write(toks[1])
                fp.write(' ')
                fp.write(toks[2])
            docids.add(toks[0])

    # entities
    entities = collections.defaultdict(list)
    with open(entities_file, encoding='utf8') as fp:
        for line in tqdm.tqdm(fp, desc=entities_file.stem):
            toks = line.strip().split('\t')
            entities[toks[0]].append('{}\t{} {} {}\t{}'.format(toks[1], toks[2], toks[3], toks[4], toks[5]))

    # relations
    relations = collections.defaultdict(list)
    relid = 0
    with open(relation_file, encoding='utf8') as fp:
        for line in tqdm.tqdm(fp, desc=relation_file.stem):
            toks = line.strip().split('\t')
            relations[toks[0]].append('R{}\t{} {} {}'.format(relid, toks[1], toks[2], toks[3]))
            relid += 1

    for docid in docids:
        with open(output_dir / '{}.ann'.format(docid), 'w', encoding='utf8') as fp:
            for ent in entities[docid]:
                fp.write(ent + '\n')
            for rel in relations[docid]:
                fp.write(rel + '\n')


if __name__ == '__main__':
    dir = Path.home() / 'Data/drugprot'
    data_dir = dir / 'drugprot-gs-training-development'
    output_dir = dir / 'brat'

    # convert(data_dir / 'training/drugprot_training_abstracs.tsv',
    #         data_dir / 'training/drugprot_training_entities.tsv',
    #         data_dir / 'training/drugprot_training_relations.tsv',
    #         output_dir / 'train.xml')

    convert(data_dir / 'development/drugprot_development_abstracs.tsv',
            data_dir / 'development/drugprot_development_entities.tsv',
            data_dir / 'development/drugprot_development_relations.tsv',
            output_dir)

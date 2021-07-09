import collections
from pathlib import Path

import bioc
import tqdm

from utils import in_one_sentence


def find_ann(annotations, id):
    for ann in annotations:
        if ann.id == id:
            return ann
    raise KeyError('{}: Cannot find ann'.format(id))


def calculate(input):
    with open(input, encoding='utf8') as fp:
        collection = bioc.load(fp)

    cnt = collections.Counter()

    # entities
    # for doc in tqdm.tqdm(collection.documents):
    #     for passage in doc.passages:
    #         for ann in passage.annotations:
    #             type = ann.infons['type']
    #             cnt[type] += 1

    # relations
    # for doc in tqdm.tqdm(collection.documents):
    #     for passage in doc.passages:
    #         for rel in passage.relations:
    #             type = rel.infons['type']
    #             # cnt[type] += 1
    #             ann1 = find_ann(passage.annotations, rel.nodes[0].refid)
    #             ann2 = find_ann(passage.annotations, rel.nodes[1].refid)
    #             if not ann1.infons['type'].startswith('CHEMICAL') or not ann2.infons['type'].startswith('GENE'):
    #                 print('relation arg types error')

    # relations in one sentence
    for doc in tqdm.tqdm(collection.documents):
        for passage in doc.passages:
            for rel in passage.relations:
                type = rel.infons['type']
                ann1 = find_ann(passage.annotations, rel.nodes[0].refid)
                ann2 = find_ann(passage.annotations, rel.nodes[1].refid)
                sen = in_one_sentence(passage, ann1, ann2)
                if sen:
                    pass
                    # cnt['one sen'] += 1
                    # cnt['one sen ' + type] += 1
                else:
                    # pass
                    # cnt['cross sen'] += 1
                    cnt[type] += 1

                # self-loop
                # chem_start = ann1.total_span.offset
                # chem_end = chem_start + ann1.total_span.length
                # gene_start = ann2.total_span.offset
                # gene_end = gene_start + ann2.total_span.length
                # if chem_start <= gene_start <= chem_end \
                #         or chem_start <= gene_end <= chem_end \
                #         or gene_start <= chem_start <= gene_end \
                #         or gene_start <= chem_end <= gene_end:
                #     cnt[type] += 1

    for k in sorted(cnt.keys()):
        print(k, cnt[k])



if __name__ == '__main__':
    dir = Path.home() / 'Data/drugprot'
    data_dir = dir / 'bioc'

    # with open(data_dir / 'train_preprocessed.xml', encoding='utf8') as fp:
    #     collection = bioc.load(fp)
    # with open(data_dir / 'train_preprocessed.xml', 'w', encoding='utf8') as fp:
    #     bioc.dump(collection, fp)

    calculate(data_dir / 'train_preprocessed.xml')




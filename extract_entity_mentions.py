import collections
from pathlib import Path

import bioc
import tqdm


def get_annotation(annotations, refid):
    for ann in annotations:
        if ann.id == refid:
            return ann
    raise ValueError


if __name__ == '__main__':
    dir = Path.home() / 'Data/drugprot'
    data_dir = dir / 'drugprot-gs-training-development'
    input_dir = dir / 'bioc'

    with open(input_dir / 'train.xml', encoding='utf8') as fp:
        collection = bioc.load(fp)

    cnt = collections.Counter()
    for doc in tqdm.tqdm(collection.documents):
        for passage in doc.passages:
            for rel in passage.relations:
                if rel.infons['type'] == 'PART-OF':
                    chem = get_annotation(passage.annotations, rel.nodes[0].refid)
                    cnt[chem.text] += 1

    for k, v in cnt.most_common():
        print('{}\t{}'.format(k, v))
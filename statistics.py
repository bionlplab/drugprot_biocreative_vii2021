import collections
from pathlib import Path

import bioc
import tqdm

from utils import in_one_sentence, find_ann


def check_entity_types(collection: bioc.BioCCollection):
    cnt = collections.Counter()

    for doc in tqdm.tqdm(collection.documents):
        for passage in doc.passages:
            for ann in passage.annotations:
                type = ann.infons['type']
                cnt[type] += 1

    for k in sorted(cnt.keys()):
        print(k, cnt[k])


def check_relation_types(collection: bioc.BioCCollection):
    cnt = collections.Counter()
    for doc in tqdm.tqdm(collection.documents):
        for passage in doc.passages:
            for rel in passage.relations:
                type = rel.infons['type']
                # cnt[type] += 1
                ann1 = find_ann(passage.annotations, rel.nodes[0].refid)
                ann2 = find_ann(passage.annotations, rel.nodes[1].refid)
                if not ann1.infons['type'].startswith('CHEMICAL') or not ann2.infons['type'].startswith('GENE'):
                    print('relation arg types error')

    for k in sorted(cnt.keys()):
        print(k, cnt[k])


def check_relation_self_loop(collection: bioc.BioCCollection):
    cnt = collections.Counter()

    # relations in one sentence
    for doc in tqdm.tqdm(collection.documents):
        for passage in doc.passages:
            for rel in passage.relations:
                pass
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


def check_relation_one_sentence(collection: bioc.BioCCollection):
    cnt = collections.Counter()
    for doc in tqdm.tqdm(collection.documents):
        for passage in doc.passages:
            for rel in passage.relations:
                type = rel.infons['type']
                ann1 = find_ann(passage.annotations, rel.nodes[0].refid)
                ann2 = find_ann(passage.annotations, rel.nodes[1].refid)
                sen = in_one_sentence(passage, ann1, ann2)
                if sen is None:
                    cnt[type] += 1
                    if ']' in ann1.text or ']' in ann2.text:
                        cnt[']'] += 1
                    else:
                        print(doc.id, rel)

    for k in sorted(cnt.keys()):
        print(k, cnt[k])


def check_sentence(collection: bioc.BioCCollection):
    cnt = collections.Counter()
    for doc in tqdm.tqdm(collection.documents):
        for passage in doc.passages:
            for sent in passage.sentences:
                if sent.text.startswith('(ABSTRACT TRUNCATED'):
                    continue
                if not sent.text.endswith('.') and not sent.text.endswith('?'):
                    cnt['sent .'] += 1
                    if sent.offset == 0:
                        cnt['sent . 0'] += 1
                    print(doc.id, sent.text)

    for k in sorted(cnt.keys()):
        print(k, cnt[k])



if __name__ == '__main__':
    dir = Path.home() / 'Data/drugprot'
    data_dir = dir / 'bioc'

    # with open(data_dir / 'train_preprocessed.xml', encoding='utf8') as fp:
    #     collection = bioc.load(fp)
    # with open(data_dir / 'train_preprocessed.xml', 'w', encoding='utf8') as fp:
    #     bioc.dump(collection, fp)

    input = data_dir / 'train_preprocessed_mergesent.xml'
    with open(input, encoding='utf8') as fp:
        collection = bioc.load(fp)

    check_relation_one_sentence(collection)




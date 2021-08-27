import collections
from pathlib import Path

import bioc
import tqdm


def get_passage_ann(doc: bioc.BioCDocument, ann: bioc.BioCAnnotation) -> bioc.BioCPassage:
    total_span = ann.total_span
    for p in doc.passages:
        if p.offset <= total_span.offset and total_span.end <= p.offset + len(p.text):
            return p
    raise KeyError('{}: {}-{}: Cannot find passage'.format(doc.id, total_span.offset, total_span.end))


def get_passage_rel(doc: bioc.BioCDocument, rel: bioc.BioCRelation) -> bioc.BioCPassage:
    ids = {rel.nodes[0].refid, rel.nodes[1].refid}
    for p in doc.passages:
        ann_ids = {ann.id for ann in p.annotations}
        if ids.issubset(ann_ids):
            return p
    print(rel)
    raise KeyError('{}: {}:{}:{}: Cannot find passage'.format(doc.id, rel.id, rel.nodes[0].refid, rel.nodes[1].refid))


def convert(abstract_file, entities_file, relation_file, output):
    collection = bioc.BioCCollection()

    cnt = collections.Counter()

    maps = {}
    with open(abstract_file, encoding='utf8') as fp:
        for line in tqdm.tqdm(fp, desc=abstract_file.stem):
            toks = line.strip().split('\t')

            doc = bioc.BioCDocument()
            doc.id = toks[0]
            collection.add_document(doc)
            maps[doc.id] = doc

            passage = bioc.BioCPassage()
            passage.text = toks[1]
            passage.offset = 0
            passage.infons['type'] = 'title'
            doc.add_passage(passage)

            passage = bioc.BioCPassage()
            passage.text = toks[2]
            passage.offset = len(toks[1]) + 1
            passage.infons['type'] = 'abstract'
            doc.add_passage(passage)

    # entities
    with open(entities_file, encoding='utf8') as fp:
        for line in tqdm.tqdm(fp, desc=entities_file.stem):
            toks = line.strip().split('\t')
            doc = maps[toks[0]]
            ann = bioc.BioCAnnotation()
            ann.id = toks[1]
            ann.infons['type'] = toks[2]
            ann.add_location(bioc.BioCLocation(int(toks[3]), int(toks[4])-int(toks[3])))
            ann.text = toks[5]

            # assert
            p = get_passage_ann(doc, ann)
            actual = p.text[ann.total_span.offset-p.offset:ann.total_span.end-p.offset]
            if actual != ann.text:
                print('{}:{}-{}:{}: Not match {}'.format(
                    doc.id, ann.total_span.offset, ann.total_span.end, ann.text, actual))
                cnt['Entity not match'] += 1
            else:
                p.add_annotation(ann)

    # relations
    if relation_file is not None and relation_file.exists():
        rel_id = 0
        with open(relation_file, encoding='utf8') as fp:
            for line in tqdm.tqdm(fp, desc=relation_file.stem):
                toks = line.strip().split('\t')
                doc = maps[toks[0]]
                rel = bioc.BioCRelation()
                rel.id = 'R{}'.format(rel_id)
                rel.infons['type'] = toks[1]
                idx = toks[2].find(':')
                rel.add_node(bioc.BioCNode(toks[2][idx + 1:], toks[2][:idx]))
                idx = toks[3].find(':')
                rel.add_node(bioc.BioCNode(toks[3][idx + 1:], toks[3][:idx]))

                # assert
                try:
                    p = get_passage_rel(doc, rel)
                    p.add_relation(rel)
                except:
                    print('{}: {}:{}:{}: Cannot find passage'.format(doc.id, rel.id, rel.nodes[0].refid, rel.nodes[1].refid))
                    cnt['cross passage ann'] += 1
                    exit(1)

                rel_id += 1

    for k, v in cnt.most_common():
        print(k, v)

    with open(output, 'w', encoding='utf8') as fp:
        bioc.dump(collection, fp)


if __name__ == '__main__':
    dir = Path.home() / 'Data/drugprot'
    data_dir = dir / 'drugprot-gs'
    output_dir = dir / 'bioc'

    # convert(data_dir / 'training/drugprot_training_abstracs.tsv',
    #         data_dir / 'training/drugprot_training_entities.tsv',
    #         data_dir / 'training/drugprot_training_relations.tsv',
    #         output_dir / 'train.xml')

    # convert(data_dir / 'development/drugprot_development_abstracs.tsv',
    #         data_dir / 'development/drugprot_development_entities.tsv',
    #         data_dir / 'development/drugprot_development_relations.tsv',
    #         output_dir / 'development.xml')

    convert(data_dir / 'test-background/test_background_abstracts.tsv',
            data_dir / 'test-background/test_background_entities.tsv',
            None,
            output_dir / 'test-background.xml')


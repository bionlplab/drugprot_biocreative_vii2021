import collections
import csv
import itertools
from pathlib import Path
from typing import List

import tqdm
import bioc

from create_drugprot_bert import find_relations
from utils import in_one_sentence, ExtendedCounter


def is_bournday2(offset, annotations: List[bioc.BioCAnnotation], chem: bioc.BioCAnnotation, gene: bioc.BioCAnnotation,
                 start):
    tags = set()
    for ann in annotations:
        is_boundary = False
        if start:
            is_boundary = ann.total_span.offset == offset
        else:
            is_boundary = ann.total_span.end == offset
        if is_boundary:
            if ann.infons['type'].startswith('CHEM'):
                if ann.id == chem.id:
                    tags.add('CHEM')
                else:
                    tags.add('CHEM_O')
            elif ann.infons['type'].startswith('GENE'):
                if ann.id == gene.id:
                    tags.add('GENE')
                else:
                    tags.add('GENE_O')
            else:
                raise KeyError(ann)
    return tags


def replace_text2(sen: bioc.BioCSentence, annotations: List[bioc.BioCAnnotation],
                  chem: bioc.BioCAnnotation, gene: bioc.BioCAnnotation):
    output_sen = ''

    i = 0
    while i < len(sen.text):
        char = sen.text[i]
        tags = is_bournday2(i + sen.offset, annotations, chem, gene, start=True)
        if len(tags) > 0:
            for t in sorted(tags):
                output_sen += '@{}-B$ '.format(t)
        output_sen += char
        tags = is_bournday2(i + 1 + sen.offset, annotations, chem, gene, start=False)
        if len(tags) > 0:
            for t in sorted(tags, reverse=True):
                output_sen += ' @{}-E$ '.format(t)
        i += 1
    return output_sen


def is_start(offset, chem: bioc.BioCAnnotation, gene: bioc.BioCAnnotation):
    if offset == chem.total_span.offset or offset == gene.total_span.offset:
        if gene.total_span in chem.total_span:
            return 'CHEM-GENE', chem
        elif chem.total_span in gene.total_span:
            return 'CHEM-GENE', gene

    if offset == chem.total_span.offset:
        return 'CHEMICAL', chem
    elif offset == gene.total_span.offset:
        return 'GENE', gene
    else:
        return None, None


def replace_text(sen: bioc.BioCSentence, chem: bioc.BioCAnnotation, gene: bioc.BioCAnnotation):
    output_sen = ''

    i = 0
    while i < len(sen.text):
        char = sen.text[i]
        status, ann = is_start(i + sen.offset, chem, gene)
        if status:
            output_sen += '@{}$'.format(status)
            i += len(ann.text)
        else:
            output_sen += char
            i += 1

    return output_sen


def is_start3(offset, annotations: List[bioc.BioCAnnotation], chem: bioc.BioCAnnotation, gene: bioc.BioCAnnotation):
    tags = []
    for ann in annotations:
        if ann.total_span.offset == offset:
            if ann.infons['type'].startswith('CHEM'):
                if ann.id == chem.id:
                    tags.append(['CHEM', ann])
                else:
                    tags.append(['CHEM_O', ann])
            elif ann.infons['type'].startswith('GENE'):
                if ann.id == gene.id:
                    tags.append(['GENE', ann])
                else:
                    tags.append(['GENE_O', ann])
            else:
                raise KeyError(ann)
    if len(tags) > 0:
        t = '-'.join(sorted(t[0] for t in tags))
        start = min(t[1].total_span.offset for t in tags)
        end = min(t[1].total_span.end for t in tags)
        return t, start, end
    else:
        return None, None, None


def replace_text3(sen: bioc.BioCSentence, annotations: List[bioc.BioCAnnotation],
                  chem: bioc.BioCAnnotation, gene: bioc.BioCAnnotation):
    output_sen = ''
    i = 0
    while i < len(sen.text):
        char = sen.text[i]
        status, start, end = is_start3(i + sen.offset, annotations, chem, gene)
        if status:
            output_sen += '@{}$'.format(status)
            i += (end - start)
        else:
            output_sen += char
            i += 1

    return output_sen


def create_drugprot_bert(input, output):
    with open(input, encoding='utf8') as fp:
        collection = bioc.load(fp)

    cnt = ExtendedCounter()

    fp = open(output, 'w', encoding='utf8')
    writer = csv.writer(fp, delimiter='\t', lineterminator='\n')
    writer.writerow(['index', 'sentence', 'label'])
    for doci, doc in enumerate(tqdm.tqdm(collection.documents)):
        for passage in doc.passages:
            chemicals = [ann for ann in passage.annotations if ann.infons['type'].startswith('CHEMICAL')]
            genes = [ann for ann in passage.annotations if ann.infons['type'].startswith('GENE')]
            for i, (chem, gene) in enumerate(itertools.product(chemicals, genes)):
                # sentence
                sentence = in_one_sentence(passage, chem, gene)
                if sentence:
                    # one sentence
                    relid = '{}.{}.{}'.format(doc.id, chem.id, gene.id)
                    text = replace_text2(sentence, passage.annotations, chem, gene)
                    cnt[1]['single sentence'] += 1
                else:
                    continue

                labels = find_relations(passage, chem, gene)
                if len(labels) == 0:
                    writer.writerow([relid, text, 'False'])
                else:
                    for l in labels:
                        writer.writerow([relid, text, l])
                        cnt[2][l] += 1
                        if '@CHEM-GENE$' in text:
                            cnt[1]['@CHEM-GENE$'] += 1
                    cnt[1]['labels ' + str(len(labels))] += 1
        # if doci > 10:
        #     break

    fp.close()

    cnt.pretty_print()


if __name__ == '__main__':
    dir = Path.home() / 'Data/drugprot'
    input_dir = dir / 'bioc'
    output_dir = dir / 'bert'

    # create_drugprot_bert(input_dir / 'development_preprocessed_mergesent.xml',
    #                      output_dir / 'development_mergesent3.tsv')
    #
    create_drugprot_bert(input_dir / 'train_preprocessed_mergesent.xml',
                         output_dir / 'train_mergesent2.tsv')

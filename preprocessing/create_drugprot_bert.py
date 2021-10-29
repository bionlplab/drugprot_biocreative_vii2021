"""
Usage:
    script <input> <output>
"""

import csv
import itertools
import os.path
import tempfile
from pathlib import Path
from zipfile import ZipFile

import docopt
import tqdm
import bioc

from utils import in_one_sentence, ExtendedCounter, FileLock, bioc_reader_zip


def find_relations(passage: bioc.BioCPassage, chem: bioc.BioCAnnotation, gene: bioc.BioCAnnotation):
    labels = []
    for rel in passage.relations:
        if rel.nodes[0].refid == chem.id and rel.nodes[1].refid == gene.id:
            labels.append(rel.infons['type'])
    return labels


def replace_text(sen: bioc.BioCSentence, chem: bioc.BioCAnnotation, gene: bioc.BioCAnnotation):
    offset = sen.offset
    text = sen.text

    chem_start = chem.total_span.offset - offset
    chem_end = chem_start + chem.total_span.length

    gene_start = gene.total_span.offset - offset
    gene_end = gene_start + gene.total_span.length

    if text[chem_start:chem_end] != chem.text:
        raise ValueError('{}: Cannot find chem {} vs {}'.format(chem.total_span.offset, text[chem_start:chem_end], chem.text))
    if text[gene_start:gene_end] != gene.text:
        raise ValueError('{}: Cannot find gene {} vs {}'.format(gene.total_span.offset, text[gene_start:gene_end], gene.text))

    if chem_start <= gene_start <= chem_end \
            or chem_start <= gene_end <= chem_end \
            or gene_start <= chem_start <= gene_end \
            or gene_start <= chem_end <= gene_end:
        start = min(chem_start, gene_start)
        end = max(chem_end, gene_end)
        before = text[:start]
        after = text[end:]
        return before + '@CHEM-GENE$' + after

    if chem_start < gene_start:
        before = text[:chem_start]
        middle = text[chem_end:gene_start]
        after = text[gene_end:]
        return before + f'@CHEMICAL$' + middle + f'@GENE$' + after
    else:
        before = text[:gene_start]
        middle = text[gene_end:chem_start]
        after = text[chem_end:]
        return before + f'@GENE$' + middle + f'@CHEMICAL$' + after


def create_drugprot_bert(input, output):
    input = Path(input)
    output = Path(output)

    lck = FileLock(output)
    if lck.exists():
        return

    with lck:
        if str(input).endswith('.zip'):
            reader = bioc_reader_zip(input)
        else:
            reader = bioc.BioCXMLDocumentReader(str(input))

        cnt = ExtendedCounter()

        fp = open(output, 'w', encoding='utf8')
        writer = csv.writer(fp, delimiter='\t', lineterminator='\n')
        writer.writerow(['index', 'sentence', 'label'])
        for doc in tqdm.tqdm(reader):
            for passage in doc.passages:
                chemicals = [ann for ann in passage.annotations if ann.infons['type'].startswith('CHEMICAL')]
                genes = [ann for ann in passage.annotations if ann.infons['type'].startswith('GENE')]
                for i, (chem, gene) in enumerate(itertools.product(chemicals, genes)):
                    # sentence
                    sentence = in_one_sentence(passage, chem, gene)
                    if sentence:
                        # one sentence
                        relid = '{}.{}.{}'.format(doc.id, chem.id, gene.id)
                        text = replace_text(sentence, chem, gene)
                        cnt[1]['single sentence'] += 1
                    else:
                        continue
                        # cross sen
                        # relid = 'c{}.{}.{}'.format(doc.id, chem.id, gene.id)
                        # text = replace_text_passage(passage, chem, gene)
                        # cnt['cross sentence'] += 1

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

        fp.close()
        # reader.close()

        cnt.pretty_print()


def process_cmd():
    argv = docopt.docopt(__doc__)
    print(argv)
    create_drugprot_bert(argv['<input>'], argv['<output>'])


def process_file():
    dir = Path.home() / 'Data/drugprot'
    input_dir = dir / 'bioc'
    output_dir = dir / 'bert'
    # create_drugprot_bert(input_dir / 'train_preprocessed_mergesent.xml', output_dir / 'train_mergesent.tsv')
    create_drugprot_bert(input_dir / 'test-background_preprocessed_mergesent.xml',
                         output_dir / 'test-background_mergesent.tsv')


if __name__ == '__main__':
    process_cmd()

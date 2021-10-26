import collections
import re


import csv
import itertools
from pathlib import Path

import tqdm
import bioc

from create_drugprot_bert import replace_text, find_relations
from utils import in_one_sentence, ExtendedCounter, find_ann

pattern1_1 = re.compile(r'\w*nucleotides?')
pattern1_2 = re.compile(r'(cytosine|adenine|adenosine|guanine|thymine|thymidine)s?', re.I)
pattern2_1 = re.compile(r'[ATGC]{2,}')
pattern2_2 = re.compile(r'CpG')
pattern3_1 = re.compile(r'(N|NH2|NH\(2,?\)|amino)')
pattern3_2 = re.compile(r'(C|COOH|carboxyl)')
pattern3_3 = re.compile(r'(hydroxyl)')
pattern4_1 = re.compile(r'[\w ]*(amino-acid|amino acid|aminoacid)s?')
pattern5_1 = re.compile(r'[ARCEHILKFPSYWVNDQGMT]\d*')
pattern5_2 = re.compile(r'(ala|arg|cys|glu|his|ile|leu|lys|phe|prro|ser|tyr|trp|val|asn|asp|gln|gly|met|thr)\d*', re.I)
pattern5_3 = re.compile(r'[a-z0-9-]*(alanine|acetylalanine|arginine|[a-z]*cysteine|glutamic acid|histidine|isoleucine|leucine'
                        r'|lysine|phenylalanine|proline|[a-z]*serine|tyrosine|[a-z]*tryptophan|valine|asparagine'
                        r'|aspartic acid|glutamine|glycine|methionine|threonine)', re.I)
pattern5_4 = re.compile(r'acetylalanine')

pp_patterns = [pattern1_1, pattern1_2,
               pattern2_1, pattern2_2,
               pattern3_1, pattern3_2, pattern3_3,
               pattern4_1,
               pattern5_1, pattern5_2, pattern5_3]


def is_pp(chem: bioc.BioCAnnotation) -> bool:
    for p in pp_patterns:
        m = p.match(chem.text)
        if m:
            return True
    return False


def create_part_of_bert(input, output):
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
                if not is_pp(chem):
                    continue
                # sentence
                sentence = in_one_sentence(passage, chem, gene)
                if sentence:
                    # one sentence
                    relid = '{}.{}.{}'.format(doc.id, chem.id, gene.id)
                    text = replace_text(sentence, chem, gene)
                    text = text.replace('@CHEMICAL$', '@PP$')
                    text = text.replace('@CHEM-GENE$', '@PP-GENE$')
                    cnt[1]['single sentence'] += 1
                else:
                    continue
                    # cross sen
                    # relid = 'c{}.{}.{}'.format(doc.id, chem.id, gene.id)
                    # text = replace_text_passage(passage, chem, gene)
                    # cnt['cross sentence'] += 1

                labels = find_relations(passage, chem, gene)
                if len(labels) == 0:
                    cnt[2]['False_False'] += 1
                    writer.writerow([relid, text, 'False'])
                else:
                    for l in labels:
                        if l == 'PART-OF':
                            writer.writerow([relid, text, l])
                            cnt[2][l] += 1
                        else:
                            cnt[2]['False'] += 1
                            writer.writerow([relid, text, 'False'])

                        if '@PP-GENE$' in text:
                            cnt[1]['@PP-GENE$'] += 1
                    cnt[1]['labels ' + str(len(labels))] += 1

    fp.close()
    # reader.close()

    cnt.pretty_print()


def test_pp_patterns(input):
    reader = bioc.BioCXMLDocumentReader(str(input))
    cnt = collections.Counter()
    for doc in tqdm.tqdm(reader, disable=True):
        for passage in doc.passages:
            for rel in passage.relations:
                if rel.infons['type'] == 'PART-OF':
                    chem = find_ann(passage.annotations, rel.nodes[0].refid)
                    if not is_pp(chem):
                        cnt[chem.text] += 1
    for k, v in cnt.most_common():
        print(k, v)


if __name__ == '__main__':
    dir = Path.home() / 'Data/drugprot'
    input_dir = dir / 'bioc'
    output_dir = dir / 'bert'

    # test_pp_patterns(input_dir / 'train_preprocessed_mergesent.xml')

    create_part_of_bert(input_dir / 'development_preprocessed_mergesent.xml',
                        output_dir / 'development_mergesent_partof.tsv')
    create_part_of_bert(input_dir / 'train_preprocessed_mergesent.xml',
                        output_dir / 'train_mergesent_partof.tsv')




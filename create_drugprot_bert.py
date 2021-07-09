import collections
import csv
import itertools
from pathlib import Path

import tqdm
import bioc

from utils import in_one_sentence

# stanza.download('en')
# nlp = stanza.Pipeline('en')


# def tokenize_text(text, id):
#     sentences = []
#     doc = nlp(text)
#     for sent in doc.sentences:
#         sentence = bioc.BioCSentence()
#         sentence.infons['filename'] = id
#         sentence.offset = sent.start_char
#         sentence.text = text[sent.start_char:sent.end_char]
#         sentences.append(sentence)
#         i = 0
#         for token in sent:
#             for t, start, end in split_punct(token.text, token.idx):
#                 ann = bioc.BioCAnnotation()
#                 ann.id = f'a{i}'
#                 ann.text = t
#                 ann.add_location(bioc.BioCLocation(start, end-start))
#                 sentence.add_annotation(ann)
#                 i += 1
#     return sentences
#
#
# def find_entities(sentence, entities, entity_type):
#     es = []
#     for e in entities:
#         if e['type'] != entity_type:
#             continue
#         if sentence.offset <= e['start'] and e['end'] <= sentence.offset + len(sentence.text):
#             es.append(e)
#     return es


def find_relations(passage: bioc.BioCPassage, chem: bioc.BioCAnnotation, gene: bioc.BioCAnnotation):
    labels = []
    for rel in passage.relations:
        if rel.nodes[0].refid == chem.id and rel.nodes[1].refid == gene.id:
            labels.append(rel.infons['type'])
    return labels


def replace_text(text: str, offset: int, chem: bioc.BioCAnnotation, gene: bioc.BioCAnnotation):
    chem_start = chem.total_span.offset - offset
    chem_end = chem_start + chem.total_span.length

    gene_start = gene.total_span.offset - offset
    gene_end = gene_start + gene.total_span.length

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


def replace_text_passage(passage: bioc.BioCPassage, chem: bioc.BioCAnnotation, gene: bioc.BioCAnnotation):
    start = min(chem.total_span.offset, gene.total_span.offset)
    end = max(chem.total_span.end, gene.total_span.end)

    enclose = False
    offset = -1
    text = ''
    for s in passage.sentences:
        if s.offset <= start <= s.offset + len(s.text):
            enclose = True
            offset = s.offset
        if enclose:
            text += s.text + ' '
        if s.offset <= end <= s.offset + len(s.text):
            enclose = False

    return replace_text(text, offset, chem, gene)


# def merge_sentences(sentences):
#     if len(sentences) == 0:
#         return sentences
#
#     new_sentences = []
#     last_one = sentences[0]
#     for s in sentences[1:]:
#         if last_one.text[-1] in """.?!""" and last_one.text[-4:] != 'i.v.' and s.text[0].isupper():
#             new_sentences.append(last_one)
#             last_one = s
#         else:
#             last_one.text += ' ' * (s.offset - len(last_one.text) - last_one.offset)
#             last_one.text += s.text
#     new_sentences.append(last_one)
#     return new_sentences


def find_sentence(passage: bioc.BioCPassage, ann: bioc.BioCAnnotation):
    total_span = ann.total_span
    for s in passage.sentences:
        if s.offset <= total_span.offset and total_span.end <= s.offset + len(s.text):
            return s
    raise KeyError()


def create_drugprot_bert(input, output):
    with open(input, encoding='utf8') as fp:
        collection = bioc.load(fp)

    cnt = collections.Counter()
    cnt2 = collections.Counter()

    fp = open(output, 'w', encoding='utf8')
    writer = csv.writer(fp, delimiter='\t', lineterminator='\n')
    writer.writerow(['index', 'sentence', 'label'])
    for doc in tqdm.tqdm(collection.documents):
        for passage in doc.passages:
            chemicals = [ann for ann in passage.annotations if ann.infons['type'].startswith('CHEMICAL')]
            genes = [ann for ann in passage.annotations if ann.infons['type'].startswith('GENE')]
            for i, (chem, gene) in enumerate(itertools.product(chemicals, genes)):
                # sentence
                sentence = in_one_sentence(passage, chem, gene)
                if sentence:
                    # one sentence
                    relid = '{}.{}.{}'.format(doc.id, chem.id, gene.id)
                    text = replace_text(sentence.text, sentence.offset, chem, gene)
                    cnt['single sentence'] += 1
                else:
                    continue
                    # cross sen
                    relid = 'c{}.{}.{}'.format(doc.id, chem.id, gene.id)
                    text = replace_text_passage(passage, chem, gene)
                    cnt['cross sentence'] += 1

                labels = find_relations(passage, chem, gene)
                if len(labels) == 0:
                    writer.writerow([relid, text, 'False'])
                else:
                    for l in labels:
                        writer.writerow([relid, text, l])
                        cnt2[l] += 1
                        if '@CHEM-GENE$' in text:
                            cnt2['@CHEM-GENE$'] += 1
                    cnt['labels ' + str(len(labels))] += 1

    fp.close()

    for k in sorted(cnt.keys()):
        print(k, cnt[k])

    print()

    for k in sorted(cnt2.keys()):
        print(k, cnt2[k])


if __name__ == '__main__':
    dir = Path.home() / 'Data/drugprot'
    input_dir = dir / 'bioc'
    output_dir = dir / 'bert'
    create_drugprot_bert(input_dir / 'train_preprocessed.xml', output_dir / 'train.tsv')
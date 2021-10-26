"""
Usage:
    script <input> <output>
"""
import os
import zipfile
from pathlib import Path
from zipfile import ZipFile

import bioc
import docopt
import tqdm

from utils import FileLock, bioc_load_zip, bioc_dump_zip


def should_merge(sent):
    if sent.text.startswith('(ABSTRACT TRUNCATED'):
        return False
    return sent.text.endswith(']') or (not sent.text.endswith('.'))


def should_merge2(sent1, sent2):
    return sent1.offset + len(sent1.text) == sent2.offset


def merge_sentences_helper(sentences):
    found = False
    new_sentences = []
    i = 0
    while i < len(sentences):
        sent = sentences[i]
        if i == len(sentences) - 1:
            pass
        else:
            next_sent = sentences[i + 1]
            if should_merge(sent) or should_merge2(sent, next_sent):
                sent.text += ' ' * (next_sent.offset - (sent.offset + len(sent.text)))
                sent.text += next_sent.text
                sent.annotations += next_sent.annotations
                sent.relations += next_sent.relations
                i += 1
                found = True
        new_sentences.append(sent)
        i += 1
    return new_sentences, found


def merge_sentences(collection: bioc.BioCCollection):
    for doc in tqdm.tqdm(collection.documents):
        for passage in doc.passages:
            new_sentences, found = merge_sentences_helper(passage.sentences)
            cnt = 0
            while found:
                new_sentences, found = merge_sentences_helper(new_sentences)
                cnt += 1
                if cnt >= 10:
                    print(doc.id)
                    for s in new_sentences:
                        print(s.offset, s.text)
                    exit(1)
            passage.sentences = new_sentences


def merge_sentences_file(input, output):
    input = Path(input)
    output = Path(output)

    lck = FileLock(output)
    if lck.exists():
        return

    with lck:
        print('Read {}'.format(input.name))
        if str(input).endswith('.zip'):
            with ZipFile(input) as myzip:
                collection = bioc_load_zip(myzip)
        else:
            with open(input, encoding='utf8') as fp:
                collection = bioc.load(fp)

        merge_sentences(collection)

        if str(output).endswith('.zip'):
            with ZipFile(output, mode='w', compression=zipfile.ZIP_DEFLATED) as myzip:
                bioc_dump_zip(collection, myzip)
        else:
            with open(output, 'w', encoding='utf8') as fp:
                bioc.dump(collection, fp)


if __name__ == '__main__':
    argv = docopt.docopt(__doc__)
    merge_sentences_file(argv['<input>'], argv['<output>'])

    # dir = Path.home() / 'Data/drugprot'
    # data_dir = dir / 'bioc'

    # merge_sentences_file(data_dir / 'train_preprocessed.xml',
    #                      data_dir / 'train_preprocessed_mergesent.xml')

    # merge_sentences_file(data_dir / 'test-background_preprocessed.xml',
    #                      data_dir / 'test-background_preprocessed_mergesent.xml')

import collections
import os
import tempfile
import zipfile
from pathlib import Path
from zipfile import ZipFile

import bioc


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def in_one_sentence(passage: bioc.BioCPassage, ann1: bioc.BioCAnnotation, ann2: bioc.BioCAnnotation):
    total_span1 = ann1.total_span
    total_span2 = ann2.total_span
    for s in passage.sentences:
        if s.offset <= total_span1.offset and total_span1.end <= s.offset + len(s.text) \
                and s.offset <= total_span2.offset and total_span2.end <= s.offset + len(s.text):
            return s
    return None


class ExtendedCounter:
    def __init__(self):
        self.counters = collections.defaultdict(collections.Counter)

    def __getitem__(self, key):
        return self.counters[key]

    def total(self, key=None):
        if key is None:
            return sum(sum(c.values()) for c in self.counters.values())
        else:
            return sum(self.counters[key].values())

    def pretty_print(self):
        for k1 in sorted(self.counters.keys()):
            print(k1)
            cnt = self.counters[k1]
            for k in sorted(cnt.keys()):
                print(' ', k, cnt[k])


def find_ann(annotations, id):
    for ann in annotations:
        if ann.id == id:
            return ann
    raise KeyError('{}: Cannot find ann'.format(id))


class FileLock:
    def __init__(self, output):
        self.output = output
        self.lck = str(output) + '.lck'

    def exists(self):
        if os.path.exists(self.lck):
            print('%s lck exists' % os.path.basename(self.lck))
            return True

        if os.path.exists(self.output):
            print('%s output exists' % os.path.basename(self.output))
            return True

        return False

    def __enter__(self):
        with open(self.lck, 'w') as _:
            pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self.lck)


def bioc_dump_zip(collection, zipfile: ZipFile):
    stem = Path(zipfile.filename).stem
    s = bioc.dumps(collection)
    zipfile.writestr(stem, s)


def bioc_load_zip(zipfile: ZipFile, name=None) -> bioc.BioCCollection:
    if name is None:
        name = zipfile.namelist()[0]
    with zipfile.open(name) as fp:
        collection = bioc.load(fp)
        return collection


def bioc_reader_zip(file, name=None, tempdir=None) -> bioc.BioCXMLDocumentReader:
    with ZipFile(file) as zipfile:
        if tempdir is None:
            tempdir = tempfile.gettempdir()
        if name is None:
            name = zipfile.namelist()[0]
        zipfile.extract(name, path=tempdir)
    reader = bioc.BioCXMLDocumentReader(os.path.join(tempdir, name))
    return reader

import collections

import bioc


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

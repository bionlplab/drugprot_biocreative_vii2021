import bioc


def in_one_sentence(passage: bioc.BioCPassage, ann1: bioc.BioCAnnotation, ann2: bioc.BioCAnnotation):
    total_span1 = ann1.total_span
    total_span2 = ann2.total_span
    for s in passage.sentences:
        if s.offset <= total_span1.offset and total_span1.end <= s.offset + len(s.text) \
                and s.offset <= total_span2.offset and total_span2.end <= s.offset + len(s.text):
            return s
    return None
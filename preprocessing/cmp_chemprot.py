"""
CPR:1     x   PART-OF
CPR:2         REGULATOR|DIRECT_REGULATOR|INDIRECT_REGULATOR
CPR3:         UPREGULATOR|ACTIVATOR|INDIRECT_UPREGULATOR
CPR4:         DOWNREGULATOR|INHIBITOR|INDIRECT_DOWNREGULATOR
CPR5:         AGONIST|AGONIST-ACTIVATOR|AGONIST-INHIBITOR
CPR6:     x   ANTAGONIST
CPR7:         MODULATOR|MODULATOR-ACTIVATOR|MODULATOR-INHIBITOR
CPR8:         COFACTOR
CPR9:         SUBSTRATE|PRODUCT_OF|SUBSTRATE_PRODUCT_OF
CPR10:        NOT
"""
from pathlib import Path

import tqdm


def get_docids(input):
    docids = set()
    with open(input, encoding='utf8') as fp:
        for line in tqdm.tqdm(fp, desc=input.stem):
            toks = line.strip().split('\t')
            docids.add(toks[0])
    return docids


def cmp_abstract():
    d_train_docids = get_docids(drugprot_dir / 'training/drugprot_training_abstracs.tsv')
    d_dev_docids = get_docids(drugprot_dir / 'development/drugprot_development_abstracs.tsv')

    c_train_docids = get_docids(chemprot_dir / 'chemprot_training/chemprot_training_abstracts.tsv')
    c_dev_docids = get_docids(chemprot_dir / 'chemprot_development/chemprot_development_abstracts.tsv')
    c_test_docids = get_docids(chemprot_dir / 'chemprot_test_gs/chemprot_test_abstracts_gs.tsv')

    d_total = d_train_docids | d_dev_docids
    c_total = c_train_docids | c_dev_docids | c_test_docids

    print('Total drugprot', len(d_total))
    print('Total chemprot', len(c_total))

    print(len(d_total - c_total))
    print(len(c_total - d_total))
    print(len(d_total & c_total))
    print(len(d_total | c_total))


if __name__ == '__main__':
    drugprot_dir = Path.home() / 'Data/drugprot/drugprot-gs-training-development'
    chemprot_dir = Path.home() / 'Data/ChemProt_Corpus/'
    cmp_abstract()

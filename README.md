## CU-UD: text-mining drug and chemical-protein interactions with ensembles of BERT-based models

### Introduction

Identifying the relations between chemicals and proteins is an important text mining task. [BioCreative VII track 1 DrugProt task](https://biocreative.bioinformatics.udel.edu/tasks/biocreative-vii/track-1/) aims to promote the development and evaluation of systems that can automatically detect relations between chemical compounds/drugs and genes/proteins in PubMed abstracts. In this work, we describe our submission, which is an ensemble system, including multiple BERT-based language models. We combine the outputs of individual models using majority voting and multilayer perceptron. 

### Datasets

The DrugProt dataset can be downloaded at [https://zenodo.org/record/5042151#.YOdvf0wpCUm](https://zenodo.org/record/5042151#.YOdvf0wpCUm)

### Results

Our system obtained 0.7708 in precision and 0.7770 in recall, for an F1 score of 0.7739, demonstrating the effectiveness of using ensembles of BERT-based language models for automatically detecting relations between chemicals and proteins.

| Run | System                         | Precision | Recall | F1-score |
|-----|--------------------------------|-----------|--------|----------|
| 1   | Stacking (MLP)                 | 0.7421    | 0.7902 | 0.7654   |
| 2   | Stacking (MLP)                 | 0.7360    | 0.7925 | 0.7632   |
| 3   | Stacking (MLP)+Majority Voting | 0.7708    | 0.7770 | 0.7739   |
| 4   | Majority Voting                | 0.7721    | 0.7750 | 0.7736   |
| 5   | BioM-ELECTRA_L                 | 0.7548    | 0.7747 | 0.7647   |

### How to use

### How to cite this work

    Karabulut ME, Vijay-Shanker K, Peng Y.
    CU-UD: text-mining drug and chemical-protein interactions with ensembles of BERT-based models.
    In BioCreative VII. 2021 (accepted)

### Acknowledgments

This work is supported by the National Library of Medicine under Award No. 4R00LM013001.

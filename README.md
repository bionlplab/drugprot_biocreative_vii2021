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

### Get started

#### Install from source

```bash
$ git clone https://github.com/bionlplab/drugprot_bcvii/
$ cd /path/to/drugprot_bcvii
$ pip install -r requirements.txt
```

#### Prepare the dataset

After downloading the Drugprot dataset (entities, relations and abstracts files), create a folder ```drugprot-gs``` under the root project directory and unzip the dataset in that folder.

Run the preprocessing script as:

```
chmod +x scripts/preprocess.sh
./scripts/preprocess.sh
```

This script will create two folders ```drugprot_data``` and ```drugprot_data_tag2``` which contain the BERT input data ```train.tsv```, ```dev.tsv```, ```test.tsv```
corresponding to the two different tagging mechanism, respectively, as described in the paper. 

#### Fine-tune individual models

You can find the pretrained models:

BioBERT: https://drive.google.com/drive/u/0/folders/1RjwQ2rgAm6W1phMJP5d1YZGMIL2dEJNX

PubMedBERT: https://drive.google.com/drive/u/0/folders/1tQFu0O0fCyZkX6WnvIphtuoGfzQz3lj6

After downloading one of the pre-trained weights, unpack it to any directory you want and change the ```PRETRAIN_DIR``` variable in ```run_finetuning.sh``` file accordingly.
We fine-tuned BioBERT and PubMedBERT on GeForce RTX 2080 Ti. Since BioM-ELECTRAL is a large model, we fine-tuned it in google colab using their free gpu/tpu service. Colab notebook for fine-tuning of BioM-ELECTRAL will be provided soon.

Update the ```DATA_DIR``` in ```run_finetuning.sh``` to indicate a folder with BERT input data. ```-output_feature=true``` writes [CLS] predictions in the output directory set.

Set ```BERT_MODEL``` variable to ```original``` to have default LM head in the BERT. Set it to ```attention_last_layer``` to add attention layer on the last layer. Set it to ```lstm_last_layer``` to add LSTM layer on the last layer. 


Default parameters will allow you fine-tune PubMedBERT with good set of parameters. 

Run the finetuning script as:
```
chmod +x run_finetuning.sh
./run_finetuning.sh
```

#### Train ensemble models

Fine-tuning any BERT model provides softmax outputs (probabilities for 14 classes) in a file ```test_features.tsv```. ```majority_voting.py``` expects five input directories with probability files, and an output directory to write the output probability file. Replace indir1 to indir 5 with actual directory names.

```
python majority_voting.py -d1 indir1 -d2 indir2 -d3 indir3 -d4 indir4 -d5 indir5 -o outdir
```

### How to cite this work

    Karabulut ME, Vijay-Shanker K, Peng Y.
    CU-UD: text-mining drug and chemical-protein interactions with ensembles of BERT-based models.
    In BioCreative VII. 2021 (accepted)

### Acknowledgments

This work is supported by the National Library of Medicine under Award No. 4R00LM013001.

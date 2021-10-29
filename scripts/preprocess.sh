#! /bin/bash

#This script runs preprocessing in four steps. drugprot_to_bioc.py > preprocess.py > postprocesses.py > create_drugprot_bert(1-2).py
#Skip any of these steps if you already had the intermediate data.

echo "Converting raw data to bioc format..."

python preprocessing/drugprot_to_bioc.py "./drugprot-gs"

echo "Preprocessing..."

python preprocessing/preprocess.py "./bioc/train.xml" "./bioc/train_preprocessed.xml"
python preprocessing/preprocess.py "./bioc/development.xml" "./bioc/development_preprocessed.xml"

python preprocessing/postprocess.py "./bioc/train_preprocessed.xml" "./bioc/train_preprocessed_mergesent.xml"
python preprocessing/postprocess.py "./bioc/development_preprocessed.xml" "./bioc/development_preprocessed_mergesent.xml"

data_dir_tag1="drugprot_data"
data_dir_tag2="drugprot_data_tag2"

data_dir1="./${data_dir_tag1}/"
data_dir2="./${data_dir_tag2}/"

mkdir -p $data_dir1
mkdir -p $data_dir2

echo "Preparing the BERT input files..."
python preprocessing/create_drugprot_bert.py "./bioc/development_preprocessed_mergesent.xml" "./${data_dir1}/dev.tsv"
python preprocessing/create_drugprot_bert.py "./bioc/development_preprocessed_mergesent.xml" "./${data_dir1}/test.tsv"
python preprocessing/create_drugprot_bert.py "./bioc/train_preprocessed_mergesent.xml" "./${data_dir1}/train.tsv"

python preprocessing/create_drugprot_bert2.py "./bioc/development_preprocessed_mergesent.xml" "./${data_dir2}/dev.tsv"
python preprocessing/create_drugprot_bert2.py "./bioc/development_preprocessed_mergesent.xml" "./${data_dir2}/test.tsv"
python preprocessing/create_drugprot_bert2.py "./bioc/train_preprocessed_mergesent.xml" "./${data_dir2}/train.tsv"

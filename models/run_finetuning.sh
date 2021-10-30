!/usr/bin/env bash

BERT_TASK="drugprot"
BERT_MODEL="original"

DATA_DIR="./drugprot_data"

PRETRAIN_DIR="./pubmedbert"

OUTPUT_DIR="./output"

mkdir -p ${OUTPUT_DIR}

for s in 2
do
    ext=${s}"/"
    SAVE_DIR="${OUTPUT_DIR}/${ext}"
    mkdir -p ${SAVE_DIR}
        python models/run_re.py --task_name=$BERT_TASK --model_name=$BERT_MODEL --do_train=true --do_eval=true --do_predict=true --vocab_file=$PRETRAIN_DIR/vocab.txt --bert_config_file=$PRETRAIN_DIR/bert_config.json --init_checkpoint=$PRETRAIN_DIR/model.ckpt --max_seq_length=256 --train_batch_size=16 --learning_rate=2e-5 --num_train_epochs=${s} --do_lower_case=true --data_dir=${DATA_DIR} --output_dir=${OUTPUT_DIR} --save_pred_dir=${SAVE_DIR}  --output_feature=true
done

#!/usr/bin/env bash
PROJECT_DIR="$(dirname "$(pwd)")"
MODEL_DIR=$1
DATA_DIR=$2
OUTPUT_DIR=$3

mkdir $OUTPUT_DIR

CUDA_VISIBLE_DEVICES=0 python $PROJECT_DIR/bert/run_ner.py --do_eval=True --do_train=False --do_predict=True \
                              --vocab_file=$MODEL_DIR/vocab.txt --bert_config_file=$MODEL_DIR/bert_config.json \
                              --init_checkpoint=$MODEL_DIR/bert_model.ckpt \
                              --num_train_epochs $4  --data_dir=$DATA_DIR  \
                              --output_dir=$OUTPUT_DIR  \
                              --save_checkpoints_steps 5000

python $PROJECT_DIR/bert/biocodes/biocodes_detok.py --gold $DATA_DIR/test.tsv --token_test $OUTPUT_DIR/token_test.txt --label_test $OUTPUT_DIR/label_test.txt  --out $OUTPUT_DIR/predicted_biobert.txt
$PROJECT_DIR/evaluation_scripts/./conlleval < $OUTPUT_DIR/predicted_biobert.txt > $OUTPUT_DIR/eval_results.txt

#!/usr/bin/env bash
PROJECT_DIR="$(dirname "$(pwd)")"
MODEL_DIR=$1
DATA_DIR=$2
OUTPUT_DIR=$3

mkdir $OUTPUT_DIR

CUDA_VISIBLE_DEVICES=0 python $PROJECT_DIR/bert/run_ner.py --do_eval=True --do_train=True --do_predict=True \
                              --vocab_file=$MODEL_DIR/vocab.txt --bert_config_file=$MODEL_DIR/bert_config.json \
                              --init_checkpoint=$MODEL_DIR/bert_model.ckpt \
                              --num_train_epochs $4  --data_dir=$DATA_DIR  \
                              --output_dir=$OUTPUT_DIR  \
                              --save_checkpoints_steps 5000

python $PROJECT_DIR/bert/biocodes/detok.py --tokens $OUTPUT_DIR/token_test.txt --label $OUTPUT_DIR/label_test.txt \
                                           --save_to $OUTPUT_DIR/predicted_biobert.txt
python $PROJECT_DIR/data_processing_utils/combine.py --test_labels $DATA_DIR/test_labels.txt \
                                                     --predicted $OUTPUT_DIR/predicted_biobert.txt \
                                                     --save_to $OUTPUT_DIR/predicted_conll.txt
$PROJECT_DIR/evaluation_scripts/./conlleval < $OUTPUT_DIR/predicted_conll.txt > $OUTPUT_DIR/eval_results.txt

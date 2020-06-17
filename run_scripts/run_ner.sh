PROJECT_DIR=/root/test_ner/chemu_competition
MODEL_DIR=/root/test_ner/med_mentions_model
DATA_DIR=/root/test_ner/processed_data_ner_tsv
OUTPUT_DIR=/tmp/quaero_tsv

mkdir $OUTPUT_DIR
cp $MODEL_DIR/label2id.pkl $OUTPUT_DIR

CUDA_VISIBLE_DEVICES=1 python $PROJECT_DIR/bert/run_ner.py --do_eval=True --do_train=False --do_predict=True --vocab_file=$MODEL_DIR/vocab.txt --bert_config_file=$MODEL_DIR/bert_config.json \
       --init_checkpoint=$MODEL_DIR/model.ckpt \
       --num_train_epochs 50.0  --data_dir=$DATA_DIR  \
       --output_dir=$OUTPUT_DIR  \
       --save_checkpoints_steps 5000

python $PROJECT_DIR/bert/biocodes/biocodes_detok.py --gold $DATA_DIR/test.tsv --token_test $OUTPUT_DIR/token_test.txt --label_test $OUTPUT_DIR/label_test.txt  --out $OUTPUT_DIR/predicted_biobert.txt
$PROJECT_DIR/evaluation_scripts/./conlleval < $OUTPUT_DIR/predicted_biobert.txt > $OUTPUT_DIR/eval_results.txt

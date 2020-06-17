PROJECT_DIR=/root/test_ner/chemu_competition
MODEL_DIR=/root/test_ner/med_mentions_model
DATA_DIR=/root/test_ner/data/BC5CDR_NCBI
OUTPUT_DIR=/tmp/BC5CDR_NCBI_tsv

mkdir $OUTPUT_DIR
cp $MODEL_DIR/label2id.pkl $OUTPUT_DIR

CUDA_VISIBLE_DEVICES=1 python $PROJECT_DIR/biobert-tsv/run_ner.py --do_eval=True --do_train=False --do_predict=True --vocab_file=$MODEL_DIR/vocab.txt --bert_config_file=$MODEL_DIR/bert_config.json \
       --init_checkpoint=$MODEL_DIR/model.ckpt \
       --num_train_epochs 50.0  --data_dir=$DATA_DIR  \
       --output_dir=$OUTPUT_DIR  \
       --save_checkpoints_steps 5000
       --batch_size 32

python $PROJECT_DIR/bert/biocodes/detok.py --tokens $OUTPUT_DIR/token_test.txt --labels $OUTPUT_DIR/label_test.txt  --save_to $OUTPUT_DIR/predicted_biobert.txt


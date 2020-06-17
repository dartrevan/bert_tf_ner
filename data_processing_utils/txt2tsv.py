f = open("/root/test_ner/processed_data_ner/train_texts.txt")
f1 = open("/root/test_ner/processed_data_ner/train_labels.txt")
out_file = open("train.tsv", "a+")
for line,line1 in zip(f,f1):
    words = line[:-1].split(" ")
    labels = line1[:-1].split(" ")
    for word,label in zip(words,labels):
        out_file.write("{}\t{}\n".format(word,label))
    out_file.write("\n")


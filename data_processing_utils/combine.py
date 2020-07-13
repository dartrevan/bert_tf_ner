from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--gold_data')
parser.add_argument('--predicted')
parser.add_argument('--save_to')
args = parser.parse_args()

def iterate_over_conll(file_path, sep=' '):
    with open(file_path, encoding="utf-8") as f:
        words = []
        labels = []
        gazetteers = []
        for line in f:
            if line.startswith("-DOCSTART-") or line == "" or line == "\n":
                if words:
                    yield words, labels, gazetteers
                    words = []
                    labels = []
                    gazetteers = []
            else:
                splits = line.split(sep)
                #replacing spaces with underscore in words
                words.append(splits[0].replace(' ', '_'))
                if len(splits) > 1:
                    labels.append(splits[1].replace("\n", ""))
                else:
                    # Examples could have no label for mode = "test"
                    labels.append("O")
                if len(splits) > 2:
                    gazetteers.append(splits[2].replace("\n", ""))
                else:
                    gazetteers.append("O")
        if words:
            yield words, labels, gazetteers

test_labels = []
for words, labels, gazetteers in iterate_over_conll(args.gold_data, sep='\t'):
  test_labels.append(labels)

pred_data = [[]]
with open(args.predicted, encoding='utf-8') as input_stream:
  for  line in input_stream:
    if len(line.strip().split(' ')) == 2:
      pred_data[-1].append(line.strip())
    else:
      pred_data.append([])
  #pred_data = input_stream.read().split('\n\n')
pred_data = pred_data[:-1]
print(len(pred_data), len(test_labels))
assert len(test_labels) == len(pred_data)
with open(args.save_to, 'w', encoding='utf-8') as output_stream:
  for pred_token_tags, true_tags in zip(pred_data, test_labels):
    for pred_toke_tag, true_tag in zip(pred_token_tags, true_tags):
      output_stream.write(pred_toke_tag + ' ' + true_tag + '\n')
    output_stream.write('\n')

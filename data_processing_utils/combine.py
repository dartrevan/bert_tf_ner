from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--test_labels')
parser.add_argument('--predicted')
parser.add_argument('--save_to')
args = parser.parse_args()

with open(args.test_labels, encoding='utf-8') as input_stream:
  test_labels = [line.strip() for line in input_stream]

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
    for pred_toke_tag, true_tag in zip(pred_token_tags, true_tags.split()):
      output_stream.write(pred_toke_tag + ' ' + true_tag + '\n')
    output_stream.write('\n')

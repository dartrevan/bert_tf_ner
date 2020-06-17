import argparse
class Detok:

    def __init__(self,golden_path,tokens,labels,save_to):
        self.golden_path = golden_path
        self.tokens = tokens
        self.labels = labels
        self.save_to = save_to

    def get_detok(self):
        tokens = []
        labels = []

        ans = dict()
        ans['toks'] = list()
        ans['labels'] = list()
        lineNoCount = 0
        with open(self.golden_path, 'r') as in_:
            for line in in_:
                line = line.strip()
                if line == '':
                    ans['toks'].append('[SEP]')
                    ans['labels'].append('O')
                    lineNoCount += 1
                    continue
                tmp = line.split()
                ans['toks'].append(tmp[0])
                ans['labels'].append(tmp[1])

        with open(self.tokens, encoding='utf-8') as tokens_input_stream, \
                open(self.labels, encoding='utf-8') as labels_input_stream:
            t_ = []
            l_ = []
            for token, label in zip(tokens_input_stream, labels_input_stream):
                token = token.strip()
                label = label.strip()
                if token == '[CLS]': continue
                if token == '[SEP]':
                    tokens.append(t_)
                    labels.append(l_)
                    t_ = []
                    l_ = []
                    continue
                if token[:2] == '##':
                    t_[-1] += token[2:]
                    continue
                t_.append(token)
                l_.append(label)
        if len(t_) != 0:
            tokens.append(t_)
            labels.append(l_)
        with open(self.save_to, 'w', encoding='utf-8') as output_stream:
            c1 = 0
            for tkns, lbls in zip(tokens, labels):
                for token, label in zip(tkns, lbls):
                    output_stream.write('{} {}-MISC {}-MISC\n'.format(token, ans['labels'][c1], label))
                    c1 += 1
                if ans['toks'][c1] == '[SEP]':
                    c1 += 1
                output_stream.write('\n')

parser = argparse.ArgumentParser()
parser.add_argument("-gold", "--gold", type=str)
parser.add_argument("-token_test", "--token_test", type=str)
parser.add_argument("-label_test", "--label_test", type=str)
parser.add_argument("-out", "--out", type=str)
args = parser.parse_args()
detok = Detok(args.gold, args.token_test,args.label_test,args.out)
detok.get_detok()

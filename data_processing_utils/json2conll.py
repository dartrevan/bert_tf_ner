import codecs
import json
import os

from nltk.tokenize import wordpunct_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
from nltk.corpus import wordnet
from nltk import pos_tag
from tqdm import tqdm
import argparse

import tokenization

class Json2conll:

    def __init__(self,in_file, out_file, entity, tagger, vocab, lower_case):
        self.in_file = in_file
        self.out_file = out_file
        self.entity = entity.split(",")
        self.tagger = tagger
        self.vocab = vocab
        self.lower_case = lower_case
        self.lemmatizer = WordNetLemmatizer()

    def get_wordnet_pos(self, treebank_tag):

        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN

    def get_token_position_in_text(self, token, w_start, text):
        start = w_start
        delimitter_start = None
        text = text.replace('й', 'и')
        text = text.replace("ё", "е")
        text = text.replace("\u00fc", "u")
        text = text.replace("\u00e5", "a")
        text = text.replace("\u03b2", "β")
        text = text.replace("\u037e", ";")
        text = text.replace("\u037e", ";")
        text = text.replace("\u03bc\u0390\u03c4\u0390", "μιτι")

        while text[w_start:w_start + len(token)] != token or (delimitter_start == None and w_start != 0):
            w_start += 1
            delimitter_start = delimitter_start or w_start
            if w_start > len(text):
                w_start = start + 2

        return w_start, w_start + len(token), text[delimitter_start:w_start]

    def get_bio_tag(self,w_start, w_end, entities, entity_type):
        for key, entity in entities.items():
            try:
                start = int(entity['start'])
                end = int(entity['end'])
            except Exception:
                raise Exception("Entity start and end must be an integer")

            if entity['entity'] in entity_type:
                if w_start > start and w_end <= end:
                    adding = entity['entity']
                    return 'I-' + adding
                elif w_start == start and w_end <= end:
                    adding = entity['entity']
                    return 'B-' + adding
        return 'O'

    def get_relation_string(self, indexes, relations):
        s = ""
        first_token = []
        second_token = []
        for key, relation in relations.items():
            try:
                start = int(relation['first_start'])
                start1 = int(relation['last_start'])
            except Exception:
                raise Exception("Token start or end must be an integer")

            for index in indexes:
                if index[0] == start:
                    first_token.append(str(index[1]))
                if index[0] == start1:
                    second_token.append(str(index[1]))
            if len(first_token) != len(second_token):
                print("")
        for i in range(len(first_token)):
            s += str(first_token[i]) + "\t" + str(second_token[i]) + "\t" + relation['type'] + "\n"
        if s != "":
            s += "\n"
        return s

    def json_to_conll(self, corpus_json_location, output_location, bio_location, entity_type, by_sent=True):
        tokenizer = tokenization.FullTokenizer(
            vocab_file=self.vocab, do_lower_case=self.lower_case)
        with codecs.open(corpus_json_location, encoding='utf-8') as in_file:
            reviews = list(map(json.loads, in_file.readlines()))
            reviews = reviews[0]['data']
            f = open(corpus_json_location)
            js_data = json.load(f)
            i = 0
        with codecs.open(output_location, 'w', encoding='utf-8') as out_file:
            for review in reviews:
                documents = sent_tokenize(review['text']) if by_sent else [review['text']]
                w_start = 0
                w_end = 0
                tokens_counter = 0
                for document in documents:
                    tokens = tokenization.make_token_list(document.split(' '), tokenizer)
                    if self.tagger == "averaged_perceptron_tagger_ru":
                        pos_tags = pos_tag(tokens, lang='rus')
                    else:
                        pos_tags = pos_tag(tokens)
                    tokens_counter += len(tokens)
                    for token, temp in zip(tokens, pos_tags):
                        token_corr = temp[0].lower()
                        print(token_corr)
                        pos = temp[1]
                        w_start, w_end, delimitter = self.get_token_position_in_text(token, w_start,
                                                                                     review['text'].lower())
                        bio_tag = self.get_bio_tag(w_start, w_end, review['entities'], entity_type)
                        lemm = self.lemmatizer.lemmatize(token_corr, self.get_wordnet_pos(pos))
                        out_file.write(
                            u'{}\t{}\n'.format(token,bio_tag))
                        w_start = w_end - 1
                js_data['data'][i]['n_token'] = tokens_counter
                out_file.write('\n')
                i += 1

    def json_to_conll2004(self, corpus_json_location, output_location, bio_location, entity_type, by_sent=False):
        tokenizer = tokenization.FullTokenizer(
            vocab_file=self.vocab, do_lower_case=self.lower_case)
        with codecs.open(corpus_json_location, encoding='utf-8') as in_file:
            reviews = list(map(json.loads, in_file.readlines()))
            reviews = reviews[0]['data']
            f = open(corpus_json_location)
            js_data = json.load(f)
            i = 0
        with codecs.open(output_location, 'w', encoding='utf-8') as out_file:
            bio_file = open(bio_location, 'a+')
            sent_count = 0

            for review in reviews:
                documents = sent_tokenize(review['text']) if by_sent else [review['text']]
                if review['index'] in [728, 828, 861, 844]:
                    continue
                w_start = 0
                w_end = 0
                for document in documents:
                    tokens = tokenization.make_token_list(document.split(' '), tokenizer)
                    if self.tagger == "averaged_perceptron_tagger_ru":
                        pos_tags = pos_tag(tokens, lang='rus')
                    else:
                        pos_tags = pos_tag(tokens)
                    tokens_counter = 0
                    starts = []
                    for token, temp in zip(tokens, pos_tags):
                        token_corr = temp[0].lower()
                        print(token_corr)
                        if token_corr == "molecular":
                            print("DEBUG")
                        if token_corr == "buchner":
                            out_file.write(u'buchner ')
                            bio_file.write(u'0 ')
                            continue
                        pos = temp[1]
                        w_start, w_end, delimitter = self.get_token_position_in_text(token, w_start,
                                                                                     review['text'].lower())
                        starts.append([w_start, tokens_counter])
                        bio_tag = self.get_bio_tag(w_start, w_end, review['entities'], entity_type)
                        lemm = self.lemmatizer.lemmatize(token_corr, self.get_wordnet_pos(pos))
                        out_file.write(
                            u'{}\t{}\t{}\tO\t{}\t{}\tO\tO\tO\n'.format(sent_count, bio_tag, tokens_counter, pos, token))
                        w_start = w_end - 1
                        tokens_counter += 1
                    out_file.write("\n")
                    out_file.write(self.get_relation_string(starts, review['relations']))
                    bio_file.write("\n")
                    sent_count += 1
                js_data['data'][i]['n_token'] = tokens_counter
                i += 1
                sent_count += 1
        os.remove(corpus_json_location)
        new_f = open(corpus_json_location, "w+")
        json.dump(js_data, new_f)

    def get_conlls(self):
        nltk.download(self.tagger)
        nltk.download('wordnet')
        nltk.download('punkt')
        self.json_to_conll(self.in_file, "data/{}.conll".format(self.out_file), "data/{}_labels.txt".format(self.out_file),
                           self.entity)

parser = argparse.ArgumentParser()
parser.add_argument("-in_json", "--in_json", type=str)
parser.add_argument("-out_conll", "--out_conll", type=str)
parser.add_argument("-entity", "--entity", type=str)
parser.add_argument("-tagger", "--tagger", type=str, default="averaged_perceptron_tagger")
parser.add_argument("-vocab_file", "--vocab_file", type=str)
parser.add_argument("-lower_case", "--lower_case", type=bool)

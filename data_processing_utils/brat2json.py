import math
import os

import pandas as pd
from sklearn.model_selection import KFold
import argparse

class Folds:

    def __init__(self, first, output, folds, out_file):
        self.first = first
        self.output = output
        self.folds = folds
        self.out_file = out_file

    def get_entity_and_slice(self,directory):
        result = []
        result_rel = []
        for filename in sorted(os.listdir(directory)):
            f = open(os.path.join(directory, filename), encoding='utf-8')
            text = f.read().lower().split("\n")
            rev = []
            rev_rel = []
            t = []
            for elem in text[:-1]:
                sentence = elem.replace("\t", " ")
                words = sentence.split(" ")
                if words[0][0] == "#":
                    continue
                if words[0][0] == "a":
                    continue
                if words[0][0] == "r":
                    first_token = words[2].split(":")[-1][1:]
                    second_token = words[3].split(":")[-1][1:]
                    for i in range(len(t)):
                        if t[i] == first_token:
                            first_index = [rev[i][1], rev[i][2]]
                        if t[i] == second_token:
                            second_index = [rev[i][1], rev[i][2]]
                        rel_type = words[1]
                    rev_rel.append([first_index[0], first_index[1], second_index[0], second_index[1], rel_type])
                    continue
                t.append(words[0][1:])
                ent = words[1:4]
                ent.append(elem.split("\t")[-1])
                rev.append(ent)
            result.append(rev)
            result_rel.append(rev_rel)
        return result, result_rel

    def get_text(self,directory):
        result = []
        names = []
        n_s = []
        for filename in sorted(os.listdir(directory)):
            f = open(os.path.join(directory, filename))
            text = f.read()
            n_sen = text.count("\n")
            text = text.replace("\n", " ")
            text = text.lower()
            result.append(text)
            names.append(filename[:-4])
            n_s.append(n_sen)
            f.close()
        return result, names, n_s

    def make_entity_dictionary(self, ent, rel, len_dataset):
        result = {}
        result_rel = {}
        for i in range(len_dataset):
            d = {}
            d_rel = {}
            for j in range(len(ent[i])):
                if ';' in ent[i][j][1]:
                    ent[i][j][1] = int(ent[i][j][1].split(";")[-1])
                if ';' in ent[i][j][2]:
                    ent[i][j][2] = int(ent[i][j][2].split(";")[-1])
                d[j] = {'start': ent[i][j][1], 'end': ent[i][j][2],
                        'entity': ent[i][j][0], 'text': ent[i][j][3]}
            for j in range(len(rel[i])):
                d_rel[j] = {'first_start': rel[i][j][0], 'first_end': rel[i][j][1],
                            'last_start': rel[i][j][2], 'last_end': rel[i][j][3], 'type': rel[i][j][4]}
            result[i] = d
            result_rel[i] = d_rel
        return result, result_rel

    def get_folds(self):
        df = pd.DataFrame(columns=['filename', 'text', 'sentences', 'entities'])
        #df = pd.DataFrame(columns=['filename', 'text'])

        text_path = os.path.join(self.first,"text")
        original_path = os.path.join(self.first,"original")

        text, names, n_s = self.get_text(text_path)
        ent_slice, rel = self.get_entity_and_slice(original_path)

        len_dataset = len(list(os.listdir(text_path)))
        entity_dict, rel_dict = self.make_entity_dictionary(ent_slice, rel, len_dataset)
        number = 0
        for i in list(entity_dict):
            df = df.append({'filename': names[i], 'text': text[i], 'sentences': n_s[i], 'entities': entity_dict[i]},
                           ignore_index=True)


        df.to_json(self.out_file, orient='table', force_ascii=False)


parser = argparse.ArgumentParser()
parser.add_argument("-input", "--input", type=str)
parser.add_argument("-out_path", "--out_path", type=str)
args = parser.parse_args() 
b2j = Folds(args.input, "data",5, args.out_path)
b2j.get_folds()


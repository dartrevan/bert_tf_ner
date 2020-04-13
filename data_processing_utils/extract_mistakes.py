from argparse import ArgumentParser
import pandas as pd
import json


def read_conll(fpath):
  tokens = []
  predicted_labels = []
  gold_labels = []
  sentence_tokens = []
  sentence_predicted_labels = []
  sentence_gold_labels = []
  with open(fpath, encoding='utf-8') as input_stream:
    for line in input_stream:
      if line == '\n':
        tokens.append(sentence_tokens[:])
        predicted_labels.append(sentence_predicted_labels[:])
        gold_labels.append(sentence_gold_labels[:])
        sentence_tokens = []
        sentence_predicted_labels = []
        sentence_gold_labels = []
      else:
        token, predicted_label, gold_label = line.strip().split()
        sentence_tokens.append(token)
        if len(sentence_predicted_labels) > 0 and sentence_predicted_labels[-1] == 'O' and  predicted_label.startswith('I-'):
          predicted_label = 'B-' + predicted_label[2:]
        sentence_predicted_labels.append(predicted_label)
        sentence_gold_labels.append(gold_label)
  if len(sentence_tokens) > 0:
    tokens.append(sentence_tokens[:])
    predicted_labels.append(sentence_predicted_labels[:])
    gold_labels.append(sentence_gold_labels[:])
  return tokens, predicted_labels, gold_labels


def extract_entities_with_spans(tokens, labels):
  entities = []
  entity = []
  sentence_entities = []
  token_id = 0
  start_token_id = 0
  end_token_id = 0
  entity_type = 'notype'
  for token, label in zip(tokens, labels):
    if (label.startswith('B-') or label == 'O') and len(entity) > 0:
      entities.append({
                        'entity_text': ' '.join(entity),
                        'start_token_id': start_token_id,
                        'end_token_id': end_token_id,
                        'entity_type': entity_type
                      })
      entity = []
    if label.startswith('B-'):
      entity.append(token)
      entity_type = label.split('-')[-1]
      start_token_id = token_id
      end_token_id = token_id
    if label.startswith('I-'):
      entity.append(token)
      entity_type = label.split('-')[-1]
      end_token_id = token_id
    token_id += 1
  return entities


def extract_entities(tokens, labels):
  entities = []
  for sentence_tokens, sentence_labels in zip(tokens, labels):
    sentence_entities = extract_entities_with_spans(sentence_tokens, sentence_labels)
    entities.append(sentence_entities[:])
  return entities


def extract(l, idx, dv=None):
  if idx < len(l):
    return l[idx]
  return dv


def span_intersect(entity_1, entity_2):
  return entity_1['start_token_id'] <= entity_2['start_token_id'] and entity_2['start_token_id'] <= entity_1['end_token_id'] or \
           entity_2['start_token_id'] <= entity_1['start_token_id'] and entity_1['start_token_id'] <= entity_2['end_token_id']


def span_match(entity_1, entity_2):
  return entity_1['start_token_id'] == entity_2['start_token_id'] and entity_1['end_token_id'] == entity_2['end_token_id']


def extract_mismatches(predicted_entities, gold_entities):
  mismatches = []
  for sentence_predicted_entities, sentence_gold_entities in zip(predicted_entities, gold_entities):
    predicted_entity_idx = 0
    gold_entity_idx = 0
    sentence_mismatches = []
    while predicted_entity_idx < len(sentence_predicted_entities) or gold_entity_idx < len(sentence_gold_entities):
      predicted_entity = extract(sentence_predicted_entities, predicted_entity_idx)
      gold_entity = extract(sentence_gold_entities, gold_entity_idx)
      if predicted_entity is None:
        sentence_mismatches.append({'gold': gold_entity, 'predicted': None, 'error_type': 'false_negative'})
        gold_entity_idx += 1
      elif gold_entity is None:
        sentence_mismatches.append({'predicted': predicted_entity, 'gold': None, 'error_type': 'false_positive'})
        predicted_entity_idx += 1
      elif span_match(predicted_entity, gold_entity):
        if predicted_entity['entity_type'] != gold_entity['entity_type']:
          sentence_mismatches.append({'predicted': predicted_entity, 'gold': gold_entity, 'error_type': 'type_mismatch'})
        predicted_entity_idx += 1
        gold_entity_idx += 1
      elif span_intersect(predicted_entity, gold_entity):
        sentence_mismatches.append({'predicted': predicted_entity, 'gold': gold_entity, 'error_type': 'span_mismatch'})
        predicted_entity_idx += 1
        gold_entity_idx += 1
      elif predicted_entity['start_token_id'] < gold_entity['start_token_id']:
        sentence_mismatches.append({'predicted': predicted_entity, 'gold': None, 'error_type': 'false_positive'})
        predicted_entity_idx += 1
      else:
        sentence_mismatches.append({'predicted': None, 'gold': gold_entity, 'error_type': 'false_negative'})
        gold_entity_idx += 1
    mismatches.append(sentence_mismatches[:])
    sentence_mismatches = []
  return mismatches


if __name__ == '__main__':
  parser = ArgumentParser()
  parser.add_argument('--conll_file')
  parser.add_argument('--document_ids')
  parser.add_argument('--save_to')
  args = parser.parse_args()
  tokens, predicted_labels, gold_labels = read_conll(args.conll_file)
  document_ids = pd.read_csv(args.document_ids, names=['document_id'], encoding='utf-8', sep='\t').document_id.tolist()
  predicted_entities = extract_entities(tokens, predicted_labels)
  gold_entities = extract_entities(tokens, gold_labels)
  #for ge in gold_entities:
  #  for e in ge:
  #    print(e['entity_text'])
  #exit()
  mismatches = extract_mismatches(predicted_entities, gold_entities)
  data = []
  prev_doc_id = None
  for sentence_mismatches, document_id in zip(mismatches, document_ids):
    if document_id != prev_doc_id:
      sentence_id = 0
    else:
      sentence_id += 1
    for mismatch in sentence_mismatches:
      predicted_entity_text = None
      gold_entity_text = None
      predicted_entity_type = None
      gold_entity_type = None
      predicted_entity_start_token_id = None
      predicted_entity_end_token_id = None
      gold_entity_start_token_id = None
      gold_entity_end_token_id = None
      error_type = mismatch['error_type']
      if error_type != 'false_negative':
        predicted_entity_text = mismatch['predicted']['entity_text']
        predicted_entity_type = mismatch['predicted']['entity_type']
        predicted_entity_start_token_id = mismatch['predicted']['start_token_id']
        predicted_entity_end_token_id = mismatch['predicted']['end_token_id']
      if error_type != 'false_positive':
        gold_entity_text = mismatch['gold']['entity_text']
        gold_entity_type = mismatch['gold']['entity_type']
        gold_entity_start_token_id = mismatch['gold']['start_token_id']
        gold_entity_end_token_id = mismatch['gold']['end_token_id']
      data.append({
                   'predicted_entity_text': predicted_entity_text,
                   'gold_entity_text': gold_entity_text,
                   'predicted_entity_type': predicted_entity_type,
                   'gold_entity_type': gold_entity_type,
                   'predicted_entity_start_token_id': predicted_entity_start_token_id,
                   'predicted_entity_end_token_id': predicted_entity_end_token_id,
                   'gold_entity_start_token_id': gold_entity_start_token_id,
                   'gold_entity_end_token_id': gold_entity_end_token_id,
                   'error_type': error_type,
                   'document_id': document_id,
                   'sentence_id': sentence_id})
    prev_doc_id = document_id

  pd.DataFrame(data).to_csv(args.save_to, index=False, encoding='utf-8', sep='\t')

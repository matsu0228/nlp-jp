# -*- coding: utf-8 -*-
import os, sys, logging, time
from gensim import corpora, matutils
from itertools import chain
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib


app_home = os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)), '..' ))
sys.path.append(os.path.join(app_home,"lib"))
from jp_parser import JpParser

LOG_LEVEL = 'DEBUG'
logging.basicConfig(
  level=getattr(logging, LOG_LEVEL),
  format='%(asctime)s [%(levelname)s] %(module)s | %(message)s',
  datefmt='%Y/%m/%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

# var
dir_name   = app_home + '/sample/data/'
save_file  = dir_name + 'gensim.dic'
model_file = dir_name + 'model.pkl'

def get_words_for_dict(feature_dic):
  """
  input: file_name of review features
          5,職場 義理チョコ パッケージ 落ち着く 感じ 年配 方 思う
  features: [[f11, f12, ...], [f21, ...], ... ]
  output: words of each sentences for gensim dict
  """
  with open(feature_dic) as filedata:
    lines = filedata.readlines()
    words = list()
    for line in lines:
      try:
        text = line.strip()
        ary = text.split(',')
        words.append(ary[1].split(' '))
      except:
        logger.error(line)
        continue
  return words

def get_meta_datasets(feature_dic):
  """
  input: file_name of review features
          5,職場 義理チョコ パッケージ 落ち着く 感じ 年配 方 思う
  features: [[f11, f12, ...], [f21, ...], ... ]
  output: [ [label, words], ... ]
  """
  with open(feature_dic) as filedata:
    lines = filedata.readlines()
    datasets = list()
    for line in lines:
      try:
        text = line.strip()
        ary = text.split(',')
        datasets.append([ ary[0], ary[1].split(' ')])
      except:
        logger.error(line)
        continue
      # TODO: tuning ex)classfy of 3 classes (pos,nue,neg)
  return datasets

def save_dic(words):
  dictionary = corpora.Dictionary(words)
  logger.info(save_file)
  dictionary.save_as_text(save_file)

def get_train_datasets(datasets):
  """
  output: words_vector of each sentence
          [[0.0, 0.1, ...], [0.1, ...], ...]
  """
  dictionary = corpora.Dictionary.load_from_text(save_file)
  vecs   = list()
  labels = list()
  for l, ws in datasets:
    try:
      # logger.info(l)
      # logger.info(ws)
      dic2bow = dictionary.doc2bow(ws)
      dense = list(matutils.corpus2dense([dic2bow], num_terms=len(dictionary)).T[0])
      # print(dense)
      vecs.append(dense)
      labels.append(l[0])
    except:
      logger.error(ws)
  return labels, vecs

def save_model(feature_dic):
  datasets = get_meta_datasets(feature_dic)
  label_train, data_train = get_train_datasets(datasets)
  # learn
  estimator = RandomForestClassifier()
  estimator.fit(data_train, label_train)
  joblib.dump(estimator, model_file)

def get_feature_for_predict(sentences):
  features = list()
  for sentence in sentences:
    jp = JpParser(sys_dic_path='/usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    f = list()
    for s in jp.filter_by_pos(sentence, pos=['NOUN', 'VERB', 'ADV'] ):
      f.append(s.base_form.lower())
      # logger.info(f)
    features.append(['temp_label' ,f])
  return features

if __name__ == "__main__":
  start = time.time()
  feature_dic = dir_name + 'feature_large.dic'
  logger.info(feature_dic)
  # words = get_words_for_dict(feature_dic)
  # save_dic(words)

  # save_model(feature_dic)
  # elapsed_time = time.time() - start
  # logger.info("set_traindata: elapsed_time:{0}".format(elapsed_time) + "[sec]")
  # logger.info(label_train)

  
  # predict
  # pred_dic = dir_name + 'feature_pred.dic'
  # pred_sets = get_meta_datasets(pred_dic)
  # label_pred, data_pred = get_train_datasets(pred_sets)
  # input: [[f11, f12, ...], [f21, ...], ... ]

  pred_file = dir_name + 'hand_reviews.txt'
  sents_pred = list()
  with open(pred_file) as filedata:
    lines = filedata.readlines()
    for line in lines:
      text = line.strip()
      ary = text.split(',')
      sents_pred.append(ary[1])

  pred_sets = get_feature_for_predict(sents_pred)
  label_pred, data_pred = get_train_datasets(pred_sets)
  estimator = joblib.load(model_file)
  label_predict = estimator.predict(data_pred)
  # display
  logger.info("\n\nresult of predict:")
  for i in range(len(label_predict)):
    logger.info(label_predict[i] + ' :' + sents_pred[i])

  elapsed_time = time.time() - start
  logger.info("end: elapsed_time:{0}".format(elapsed_time) + "[sec]")

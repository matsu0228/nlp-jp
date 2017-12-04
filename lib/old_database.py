# -*- coding: utf-8 -*-
import os, sys, logging, time, configparser
from pymongo import MongoClient,  DESCENDING
import pandas as pd
app_home = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

sys.path.append(os.path.join(app_home, "lib"))
from trans import Trans
trans = Trans()

POS_DIC = {
  'BOS/EOS': 'EOS', # end of sentense
  '形容詞' : 'ADJ',
  '副詞'   : 'ADV',
  '名詞'   : 'NOUN',
  '動詞'   : 'VERB',
  '助動詞' : 'AUX',
  '助詞'   : 'PART',
  '連体詞' : 'ADJ', # Japanese-specific POS
  '感動詞' : 'INTJ',
  '接続詞' : 'CONJ',
  '*'      : 'X',
}
LOG_LEVEL = 'DEBUG'
logging.basicConfig(
  level=getattr(logging, LOG_LEVEL),
  format='%(asctime)s [%(levelname)s] %(module)s | %(message)s',
  datefmt='%Y/%m/%d %H:%M:%S',
)

logger = logging.getLogger(__name__)
# Const of database name
POLITELY_DICT_DB = "politely_dict"
NPTABLE_COLLECTION_NAME = "np_table"
SENTIDIC_COLLECTION_NAME = "sent_dic"

# NAMING CONVENTIONS:
# "get" - should be a fast find() or find_one()
# "load" - potentially slow find() that usually returns a large set of data
# "init" - called once and only once when the collection is created
#          (usually for setting indexes)
# "save" - fast update() or update_one(). Avoid using insert() as much
#          as possible, because it is not idempotent.


def get_db(db_name):
  config = configparser.ConfigParser()
  config.read(app_home + '/myvenv/lib/config.ini')
  client = MongoClient('localhost')
  client['admin'].authenticate(config.get('mongo', 'id'), config.get('mongo', 'password'))
  # client = get_MongoClient()
  db = client[db_name]
  return db

def load_politly_dic(collection_name):
    db = get_db(POLITELY_DICT_DB)
    cursor = db[collection_name].find()
    df = pd.DataFrame.from_dict(list(cursor)).astype(object)
    # df = df[df['source'] != 'walmart'] 
    # df['review_date'] = pd.to_datetime(df['review_date'])
    # df = df.replace(np.nan, ' ')
    return df


# pn_table
# pol_file = app_home + '/dataset/posneg_dic/pn_table.dic'
def init_politely_table(file_name):
  # load file
  logger.info(file_name)
  with open(file_name) as filedata:
    lines = filedata.readlines()
    for line in lines:
      try:
        text = line.strip()
        #優れる:すぐれる:動詞:1
        data = text.split(':')
        logger.info( data )
        # save
        db = get_db(POLITELY_DICT_DB)
        # TODO: set eng
        db[NPTABLE_COLLECTION_NAME].update({'headword':data[0], 'POS_jp':data[2] },
                                           {'$set':{'headword':data[0], 'reading':data[1], 'POS':POS_DIC[data[2]], 'POS_jp':data[2], 'posneg':data[3], 'eng':''}},
                                           upsert=True)
      except:
        logger.error(data)
        continue


def get_politely_score(headword, *, pos='*'):
  db = get_db(POLITELY_DICT_DB)
  # logger.info(headword)
  # TOOD: if pos == '*' else
  res = db[NPTABLE_COLLECTION_NAME].find_one({'headword':headword}, {'posneg':1, '_id':0})
  if res == None:
    res = db[NPTABLE_COLLECTION_NAME].find_one({'reading':headword}, {'posneg':1, '_id':0})

  score = 0
  if res:
    # tuning
    if (-0.5 < float(res['posneg']) and float(res['posneg']) < 0):
      score = 0
    else:
      score = float(res['posneg'])
  return score

# senti_dic
# ==> dataset/posneg_dic/sent_nouns.dic <==
# 13314 lines 
# headword  label(p>e>n)  detail
# "２，３日"	e	〜である・になる（状態）客観
# ==> dataset/posneg_dic/sent_verb_adj.dic <==
# 5277 lines
# あがく  n  ネガ（経験）

def init_senti_dic(file_name, data_type):
  # load file
  logger.info(file_name)
  with open(file_name) as filedata:
    lines = filedata.readlines()
    for line in lines:
      try:
        # headword  label(p>e>n)  detail
        # "２，３日"	e	〜である・になる（状態）客観
        text = line.strip()
        data = text.split("\t")
        # logger.info( data )
        # get score
        score = 0
        if data[1] == 'p':
          score = 1
        elif data[1] == 'n':
          score = -1
        # save
        db = get_db(POLITELY_DICT_DB)

        # TODO: set eng / too slow
        # eng = erans.ed('/usr/local/cai_venv/lib/config.-1ini')rans_ja2en(data[0])
        eng = ''
        # logger.info({'headword':data[0], 'type':data_type, 'detail':data[2], 'score':score, 'eng':trans.trans_ja2en(data[0])})
        db[SENTIDIC_COLLECTION_NAME].update({'headword':data[0]},
                                           {'$set':{'headword':data[0], 'type':data_type,\
                                                    'detail':data[2], 'score':score, 'eng':eng}},
                                           upsert=True)
      except:
        logger.error(data)
        continue

# TODO: multi word (ex.あきれる た
def get_sentidic_score(headword, *, type=None):
  db = get_db(POLITELY_DICT_DB)
  # TODO: type
  res = db[SENTIDIC_COLLECTION_NAME].find_one({'headword':headword})
  logger.info(res)
  score = 0
  if res:
    score = res['score']
  return score

if __name__ == "__main__":
  pd = load_politly_dic(SENTIDIC_COLLECTION_NAME)
  print(pd.shape, pd.head(10))

  # db[NPTABLE_COLLECTION_NAME].update({'headword':'優れる', 'POS_jp':'動詞' },
  #                                    {'$set':{'headword':'優れる', 'reading': 'すぐれる', 'POS':'VERB', 'POS_jp':'動詞', 'eng':'be excellent'}},
  #                                    upsert=True)

  senti_file_noun = app_home + '/dataset/posneg_dic/sent_nouns.dic'
  # init_senti_dic(senti_file_noun, 'NOUN')
  senti_file_verb = app_home + '/dataset/posneg_dic/sent_verb_adj.dic'
  # get_sentidic_score('ない')
  # get_sentidic_score('合う')
  # get_sentidic_score('おいしい')
  get_sentidic_score('無い')
  get_sentidic_score('無駄')


  # init_senti_dic(senti_file_verb, 'VERB')
  # logger.info('優れる')
  # logger.info(get_politely_score('優れる') )
  # logger.info('だめ')
  # logger.info(get_politely_score('だめ') )
  # logger.info('いい')
  # logger.info(get_politely_score('いい') )
  #
  # db = get_db(POLITELY_DICT_DB)
  # res = db[NPTABLE_COLLECTION_NAME].find()
  # res = db[NPTABLE_COLLECTION_NAME].find({'headword':'優れる'})
  # for r in res:
  #   logger.info(r)


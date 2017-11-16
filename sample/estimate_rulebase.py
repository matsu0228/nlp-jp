# -*- coding: utf-8 -*-
import os, sys, logging, time

# dataset/posneg_dic/pn_ja.dic

app_home = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.append(os.path.join(app_home, "lib"))
from jp_parser import JpParser
from trans import Trans
from database import get_db, get_sentidic_score #get_politely_score

LOG_LEVEL = 'DEBUG'
logging.basicConfig(
  level=getattr(logging, LOG_LEVEL),
  format='%(asctime)s [%(levelname)s] %(module)s | %(message)s',
  datefmt='%Y/%m/%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

argvs = sys.argv
target_sentence = ''
if len(argvs) != 2:
  logger.error( 'set analysis sentence')
else:
  target_sentence = argvs[1]

jp = JpParser( sys_dic_path='/usr/local/lib/mecab/dic/mecab-ipadic-neologd')
trans = Trans()
def eval_senti_score(words):
  score = 0
  num_all_words = 0
  for w in words:
    # TODO: multi words
    s = get_sentidic_score(w)
    num_all_words += 1
    if s != 0:
      logger.info(w + str(s))
    score += s
    # round=lambda x:(x*2+1)//2
  return round(score/num_all_words, 2)

def senti_analisys(sentence):
  """
  output: score
  """
  words = list()
  for s in jp.tokenize(sentence):
    if s.base_form != '*':
      words.append(s.base_form.lower())
  score = eval_senti_score(words)
  return score

# INPUT:
# 5 __SEP__ 職場の義理チョコです
def search_lines(file_name):
  logger.info(file_name)
  if target_sentence != '':
    score = senti_analisys(target_sentence)
    print(score, target_sentence, trans.trans_ja2en(target_sentence))
  else:
    with open(file_name ) as filedata:
      lines = filedata.readlines()
      for line in lines:
        try:
          text = line.strip()
          # text = filedata.read()
          line_ary = text.split(' __SEP__ ')
          # logger.info(line_ary)
          sentence = line_ary[1]
        except:
          logger.error(line)
          continue
        score = senti_analisys(sentence)
        print(score, sentence, trans.trans_ja2en(sentence))

if __name__ == "__main__":
  start = time.time()
  file_name = app_home + '/dataset/rakuten/src/small.aa'
  # target_dir = app_home + '/dataset/rakuten/'
  search_lines(file_name)

  elapsed_time = time.time() - start
  logger.info("elapsed_time:{0}".format(elapsed_time) + "[sec]")
  # 優れる:すぐれる:動詞:1


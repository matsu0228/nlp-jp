# -*- coding: utf-8 -*-

import os, sys, logging, time
app_home = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.append(os.path.join(app_home, "lib"))
from jp_parser import JpParser
from database import get_db, get_sentidic_score #get_politely_score

class JpSentiment:
  def __init__(self):
    self._jp = JpParser(sys_dic_path='/usr/local/lib/mecab/dic/mecab-ipadic-neologd')

  def senti_tokenize(self, sentence):
    senti_tokens = {'pos':[], 'nue':[], 'neg':[]}
    for s in self._jp.tokenize(sentence):
      w = s.base_form.lower()
      # score
      if w!='*' and s.pos!='X':
        score = get_sentidic_score(w)
      else:
        continue
      # tokenize
      if score > 0:
        key = 'pos'
      elif score == 0:
        key = 'nue'
      elif score < 0:
        key = 'neg'
      else:
        print('EEROR:' + w)
      senti_tokens[key].append(w)
    return senti_tokens

if __name__ == "__main__":
  sentence = '２種類で５袋となっていて、残念でした。好みが合わなかったものは無駄になってしまいます。'
  js = JpSentiment()
  ts = js.senti_tokenize(sentence)
  print(ts)

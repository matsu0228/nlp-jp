# MeCab: Yet Another Part-of-Speech and Morphological Analyzer
# http://taku910.github.io/mecab/
# https://github.com/taku910/mecab

import MeCab
from collections import namedtuple
# import numpy as np
# import pandas as pd


class JpParser:
  """
  return parsed data with Mecab
  """
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

  def __init__(self, * ,sys_dic_path=''):
    option = "-Ochasen"
    # sys_dic_path='/usr/local/lib/mecab/dic/mecab-ipadic-neologd'
    # https://github.com/neologd/mecab-ipadic-neologd/
    if sys_dic_path:
      option += ' -d {0}'.format(sys_dic_path)
    tagger = MeCab.Tagger(option)
    tagger.parse('') # for UnicodeDecodeError
    self._tagger = tagger

  def split_into_words(self):
    return self._tagger.parse( self.text )

  def tokenize(self, sent):
    node = self._tagger.parseToNode( sent )
    while node:
      feature = node.feature.split(',')
      token = namedtuple('Token', 'surface, pos, pos_detail1, pos_detail2, pos_detail3,\
                          infl_type, infl_form, base_form, reading, phonetic')
      token.surface     = node.surface  # 表層形
      token.pos_jp      = feature[0]    # 品詞
      token.pos_detail1 = feature[1]    # 品詞細分類1
      token.pos_detail2 = feature[2]    # 品詞細分類2
      token.pos_detail3 = feature[3]    # 品詞細分類3
      token.infl_type   = feature[4]    # 活用型
      token.infl_form   = feature[5]    # 活用形
      token.base_form   = feature[6]    # 原型
      token.pos         = self.POS_DIC.get( feature[0], 'X' )     # 品詞
      token.reading     = feature[7] if len(feature) > 7 else ''  # 読み
      token.phonetic    = feature[8] if len(feature) > 8 else ''  # 発音
      yield token
      node = node.next

  def filter_by_pos(self, sent, pos=['NOUN',]):
    tokens = [token for token in self.tokenize(sent) if token.pos in pos]
    return tokens


if __name__ == "__main__":
  jp = JpParser( sys_dic_path='/usr/local/lib/mecab/dic/mecab-ipadic-neologd')
  # print( jp.split_into_words() )
  sent_data = jp.tokenize( "国立新美術館に行った。攻殻機動隊が好きです") 
  for s in sent_data:
    print(s.surface, s.base_form, s.pos)
  for n in  jp.filter_by_pos( "国立新美術館に行って、攻殻機動隊の展示をみました" ):
    print('N:', n.surface )



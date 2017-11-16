# -*- coding: utf-8 -*-

# MeCab: Yet Another Part-of-Speech and Morphological Analyzer
# - http://taku910.github.io/mecab/
# - https://github.com/taku910/mecab

# Cabocha: Yet Another Japanese Dependency Structure Analyzer
# - https://taku910.github.io/cabocha/

import MeCab
import CaboCha
from collections import namedtuple

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

  # ex) sys_dic_path='/usr/local/lib/mecab/dic/mecab-ipadic-neologd'
  # https://github.com/neologd/mecab-ipadic-neologd/
  def __init__(self, * ,sys_dic_path=''):
    opt_m = "-Ochasen"
    opt_c = '-f4'
    if sys_dic_path:
      opt_m += ' -d {0}'.format(sys_dic_path)
      opt_c += ' -d {0}'.format(sys_dic_path)
    tagger = MeCab.Tagger(opt_m)
    tagger.parse('') # for UnicodeDecodeError
    self._tagger = tagger
    self._parser = CaboCha.Parser(opt_c)

  # def split_into_words(self):
  #   return self._tagger.parse( self.text )

  def get_sentences(self, text):
    """ 
    input: text have many sentences
    output: ary of sentences ['sent1', 'sent2', ...]
    """
    EOS_DIC = ['。', '．', '！','？','!?', '!', '?' ]
    sentences = list()
    sent = ''
    for token in self.tokenize(text):
      # print(token.pos_jp, token.pos, token.surface, sent)
      # TODO: this is simple way. ex)「今日は雨ね。」と母がいった
      sent += token.surface
      if token.surface in EOS_DIC and sent != '':
        sentences.append(sent)
        sent = ''
    return sentences

  def tokenize(self, sent):
    node = self._tagger.parseToNode( sent )
    tokens = list()
    idx = 0
    while node:
      feature = node.feature.split(',')
      token = namedtuple('Token', 'idx, surface, pos, pos_detail1, pos_detail2, pos_detail3,\
                          infl_type, infl_form, base_form, reading, phonetic')
      token.idx         = idx
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
      #
      tokens.append(token)
      idx += 1
      node = node.next
    return tokens

  def filter_by_pos(self, sent, pos=['NOUN',]):
    tokens = [token for token in self.tokenize(sent) if token.pos in pos]
    return tokens

  def get_chunk_data(self, sentence):
    tree = self._parser.parse(sentence)
    tokens = self.tokenize(sentence)
    chunk_data = list()
    for i in range(0, tree.chunk_size()):
      chunk = namedtuple('Chunk', 'tokens, head_token, link, head_idx, func_idx,\
                          token_size, token_dix, feature_size, score, additional_info')
      c = tree.chunk(i)
      c_tokens = list()
      for j in range(c.token_pos, c.token_pos+c.token_size):
        c_tokens.append(tokens[j+1]) # for BOS
      chunk.tokens       = c_tokens
      chunk.head_token   = c_tokens[c.head_pos]
      chunk.link         = c.link
      chunk.head_idx     = c.head_pos
      chunk.func_idx     = c.func_pos
      chunk.token_size   = c.token_size
      chunk.token_idx    = c.token_pos
      chunk.feature_size = c.feature_list_size
      chunk.score        = c.score
      chunk.additional_info = c.additional_info
      chunk_data.append(chunk)
    return chunk_data

  def debug(self, sentence):
    tree = self._parser.parse(sentence)
    # 0: tree format
    print(tree.toString(0))
    # 4: CONLL format
    print(tree.toString(4))

if __name__ == "__main__":
  jp = JpParser( sys_dic_path='/usr/local/lib/mecab/dic/mecab-ipadic-neologd')
  # print( jp.split_into_words() )
  
  # Japanese famous poem written by Soseki natusme.
  # sentences = jp.get_sentences('我輩は猫である。名前はまだ無い。どこで生れたかとんと見当けんとうがつかぬ。何でも薄暗いじめじめした所でニャーニャー泣いていた事だけは記憶している。吾輩はここで始めて人間というものを見た。')
  sentences = jp.get_sentences('チョコが甘くて好きです。２種類で５袋となっていて、残念でした。好みが合わなかったものは無駄になってしまいます。')
  print(sentences)
  for sent in sentences:
    # token --------------------------------------
    # sent_data = jp.tokenize(sent)
    # for s in sent_data:
    #   print(s.surface, s.base_form, s.pos)

    # chunk --------------------------------------
    jp.debug(sent)
    chunk_data = jp.get_chunk_data(sent)
    for c in chunk_data:
      print(c.link, len(c.tokens), 
            'dst='+chunk_data[c.link].head_token.surface, 
            'src='+c.tokens[0].surface )
      # extract feature with dependence
      for t in c.tokens:
        if t.base_form == 'チョコ':
          feature = chunk_data[c.link].head_token.base_form
          print('チョコの特徴=' + feature)


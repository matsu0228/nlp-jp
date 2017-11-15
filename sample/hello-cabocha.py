# -*- coding: utf-8 -*-
import CaboCha

class JpParser:
  def __init__(self):
    self._parser = CaboCha.Parser('-f4') # f1

  def get_token(self, sentence):
    tree = self._parser.parse(sentence)
    print('token_size:'+str(tree.token_size()))
    for i in range(0, tree.token_size()):
      token = tree.token(i)
      print('surface:', token.surface)
      print(token.normalized_surface)
      print(token.feature)


  def get_chunk_data(self, sentence):
    tree = self._parser.parse(sentence)
    print('chunk_size:'+str(tree.chunk_size()))
    print( 'c_link', 'c_hpos', 'c_fpos', 'c_tsize', 'c_fsize')
    for i in range(0, tree.chunk_size()):
      chunk = tree.chunk(i)
      c_link = chunk.link
      c_hpos = chunk.head_pos
      c_fpos = chunk.func_pos
      c_tsize = chunk.token_size
      c_token_pos = chunk.token_pos
      c_fsize = chunk.feature_list_size
      # chunk.score
      # chunk.additional_info
      print( c_link, c_hpos, c_fpos, c_tsize, c_fsize)

  def debug(self, sentence):
    tree = self._parser.parse(sentence)
    # tree format
    print(tree.toString(0))
    # CONLL format
    print(tree.toString(4))


raw_string = u'警察官が自転車で逃げる泥棒を追いかけていた'
cp = JpParser()
cp.debug(raw_string)
cp.get_chunk_data(raw_string)
cp.get_token(raw_string)


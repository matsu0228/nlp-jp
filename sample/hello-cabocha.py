# -*- coding: utf-8 -*-
import CaboCha
import itertools

def chunk_by(func, col):
  '''
  `func`の要素が正のアイテムで区切る
  '''
  result = []
  for item in col:
    if func(item):
      result.append([])
    else:
      result[len(result) - 1].append(item)
      return result

def has_chunk(token):
  '''
  チャンクがあるかどうか
  チャンクがある場合、その単語が先頭になる
  '''
  return token.chunk is not None

def to_tokens(tree):
  '''
  解析済みの木からトークンを取得する
  '''
  return [tree.token(i) for i in range(0, tree.size())]

def concat_tokens(i, tokens, lasts):
  '''
  単語を意味のある単位にまとめる
  '''
  if i == -1:
    return None
  word = tokens[i].surface
  last_words = map(lambda x: x.surface, lasts[i])
  return word + ''.join(last_words)

raw_string = u'東京のラーメン屋がいつも混雑しているわけではない'
cp = CaboCha.Parser('-f1')
tree = cp.parse(raw_string)
tokens = to_tokens(tree)
print( tree.chunk )
head_tokens = filter(has_chunk, tokens)
print( head_tokens)
words = map(lambda x: x.surface, head_tokens)

lasts = chunk_by(has_chunk, tokens)

links = map(lambda x: x.chunk.link, head_tokens)
link_words = map(lambda x: concat_tokens(x, head_tokens, lasts), links)

for (i, to_word) in enumerate(link_words):
  from_word = concat_tokens(i, head_tokens, lasts)
  print("{0} => {1}".format(from_word, to_word))





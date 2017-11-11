# -*- coding: utf-8 -*-
import os, sys, logging
from gensim import corpora


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

argvs = sys.argv
if len(argvs) != 2:
  logger.error( 'set output file name ')
target_file = argvs[1]

def extract_noun(dir_name):
  jp = JpParser( sys_dic_path='/usr/local/lib/mecab/dic/mecab-ipadic-neologd')
  for f in os.listdir(dir_name ):
    logger.info(f)
    # debug:
    if f == 'it-life-hack-6295722.txt':
      break

    with open(dir_name + f ) as filedata:
      text = filedata.read()
      nouns = list()
      for s in jp.filter_by_pos(text, 'NOUN'):
        nouns.append( s.base_form.lower() )
      if len(nouns) > 0:
        print(f + ',' + ','.join(nouns) )


def get_noun_ary(dir_name):
  jp = JpParser( sys_dic_path='/usr/local/lib/mecab/dic/mecab-ipadic-neologd')
  nouns = list()
  for f in os.listdir(dir_name ):
    logger.info(f)
    # debug:
    if f == 'it-life-hack-6294574.txt':
      break

    with open(dir_name + f ) as filedata:
      text = filedata.read()
      n = list()
      for s in jp.filter_by_pos(text, 'NOUN'):
        n.append( s.base_form.lower() )
      nouns.append( n )
  return nouns

if __name__ == "__main__":
  dir_name = app_home + '/dataset/ldcc/it-life-hack/' 
  # extract_noun(dir_name)
  words = get_noun_ary(dir_name)
  # print(words)
  dictionary = corpora.Dictionary(words)
  save_file = dir_name + target_file
  logger.info(save_file)
  dictionary.save_as_text( save_file )
  # dictionary = corpora.Dictionary.load_from_text('livedoordic.txt')

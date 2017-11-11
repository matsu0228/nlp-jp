# -*- coding: utf-8 -*-
import os, sys, logging, time
from gensim import corpora


app_home = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.append(os.path.join(app_home, "lib"))
from jp_parser import JpParser

LOG_LEVEL = 'DEBUG'
logging.basicConfig(
  level=getattr(logging, LOG_LEVEL),
  format='%(asctime)s [%(levelname)s] %(module)s | %(message)s',
  datefmt='%Y/%m/%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

# argvs = sys.argv
# if len(argvs) != 2:
#   logger.error( 'set output file name ')
# target_file = argvs[1]


# prepare 
def conv_char( sent ):
  sent = sent.replace(',', '，')
  sent = sent.replace(' ', '　')
  return sent

# INPUT:
# 5 __SEP__ 職場の義理チョコです
def extract_feature(file_name):
  jp = JpParser( sys_dic_path='/usr/local/lib/mecab/dic/mecab-ipadic-neologd')
  logger.info(file_name)
  with open(file_name ) as filedata:
    lines = filedata.readlines()
    for line in lines:
      try:
        text = line.strip()
        # text = filedata.read()
        line_ary  = text.split(' __SEP__ ')
        logger.info(  line_ary)
        features = list()
        for s in jp.filter_by_pos( conv_char(line_ary[1]), pos=['NOUN', 'VERB', 'ADV'] ):
          features.append( s.base_form.lower() )
        logger.info(  features )
        if len(features) > 0:
          print(line_ary[0] + ',' + ' '.join(features) )
      except:
        logger.error( line )
        continue

if __name__ == "__main__":
  start = time.time()
  file_name  = app_home + '/dataset/rakuten/src/rakuten_reviews.txt'
  # target_dir = app_home + '/dataset/rakuten/'
  extract_feature(file_name)

  elapsed_time = time.time() - start
  logger.info("elapsed_time:{0}".format(elapsed_time) + "[sec]")
